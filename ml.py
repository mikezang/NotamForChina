from datetime import datetime, timedelta
from math import acos, cos, degrees, floor, pi, sin
import sys
from timeit import timeit
from pathlib import Path

from myModules import myConfig
from myModules import myExcept
from myModules import myMath

# ============================================================
# Configuration
# ============================================================
# GEOD = Geod(ellps="WGS84")

HISTORY_DIR = Path("./histories/")
KMLS_DIR = HISTORY_DIR / "kmls/"
PREDICT_DIR = HISTORY_DIR / "predict/"
TEMP_DIR = Path("./temp/")
DOWNLOAD_DIR = Path("c:/Users/w802479/Downloads")

IOU_KML_NAMES_CSV = HISTORY_DIR / "kml_names-IoU.csv"
IOU_FEATURE_CSV = HISTORY_DIR / "feature-IoU_database.csv"
IOU_FEATIRE_PKL = HISTORY_DIR / "feature-IoU_target-BINARY_model.pkl"

GEO_KML_NAMES_CSV = HISTORY_DIR / "kml_names-GEO.csv"
GEO_FEATURE_CSV = HISTORY_DIR / "feature-GEO_database.csv"
GEO_FEATIRE_PKL = HISTORY_DIR / "feature-GEO_target-BINARY_model.pkl"

# GEO_SITE_ROCKET_FEATURE_CSV = HISTORY_DIR / "feature-GEO_target-CLASSES_database.csv"
GEO_SITE_ROCKET_FEATIRE_PKL = HISTORY_DIR / "feature-GEO_target-CLASSES_model.pkl"

MODEL_RADNOM_FOREST = "RF"
MODEL_EXTRA_TREES = "ET"
MODEL_HIST_GRADIENT_BOOSTING = "HGB"
MODEL_GRADIENT_BOOSTING = "GB"

MODEL_RANDOM_STATE = 42
MIN_DATE_COVERAGE = 0.8

# SPLIT_MODE_ALL = "all"                  # use all historical launches for production predict    
SPLIT_MODE_SITE_ROCKET = "site+rocket"  # use oldest 80% trani and 20% test for site+rocket hitorical files 

COMMAND_TRAIN = "train"
COMMAND_DETECT = "detect"
COMMAND_BUILD = "build"
COMMAND_PREDICT = "predict"

UNKNOWN = "Unknown"

# ============================================================
# Save Route Angles to csv file
# ============================================================
def saveRouteAngles(routeAngles, csvFile):
    import csv
    with open(csvFile, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["site", "rocket", "route_angles"])

        for (site, rocket), angles in routeAngles.items():
            writer.writerow([site, rocket, ",".join(str(angle) for angle in angles)])

# ============================================================
# Load Route Angles from csv file
# ============================================================
def loadRouteAngles(csvFile):
    routeAngles = {}

    import csv
    with open(csvFile, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            key = (row["site"], row["rocket"])
            angles = [float(angle) for angle in row["route_angles"].split(",") if angle]
            routeAngles[key] = angles
    return routeAngles

# ------------------------------------------------------------
# 7. Build new DataFrame
# 8. Update feature database
# 9. Save feature database
# 10. Save KML cache
# 12. Summary
# ------------------------------------------------------------
def update_geo_featrure_database(new_geo_rows, old_geo_df, geo_feature_file, force_rebuild_geo, updated_cache, isSiteRocket=False):
    import pandas as pd

    if new_geo_rows:
        new_geo_df = pd.DataFrame(new_geo_rows)
        first_columns = ["target", "file", "site", "rocket", "angle_diff"]
        other_columns = [col for col in new_geo_df.columns if col not in first_columns]
        new_geo_df = new_geo_df[first_columns + other_columns]
    else:
        new_geo_df = pd.DataFrame()

    # 8. Update feature database
    # For modified KMLs:
    #     remove old row first
    #     then add newly parsed row
    if old_geo_df is None:
        geo_df = new_geo_df.copy()
    elif not new_geo_df.empty:
        updated_files = set(new_geo_df["file"].astype(str))
        # Keep all old launches EXCEPT files that were successfully re-parsed.
        old_remaining = old_geo_df[~old_geo_df["file"].astype(str).isin(updated_files)].copy()
        geo_df = pd.concat([old_remaining, new_geo_df], ignore_index=True)
    else:
        geo_df = old_geo_df.copy()

    # 9. Save feature database
    if old_geo_df is None or not new_geo_df.empty:
        geo_df.to_csv(geo_feature_file, index=False, encoding="utf-8-sig")
        print(f"\nHistorical launch files: {len(geo_df)}")
        print(f"GEO Feature database saved to: {geo_feature_file}")
    else:
        print("\nGEO Feature database unchanged.")

    if new_geo_rows:
        # 10. Save KML cache
        # Cache contains:
        #     file
        #     modified_time
        # Only successfully parsed new/modified files update
        # their timestamps.
        cache_rows = [{"file": file_name, "modified_time": modified_time} for file_name, modified_time in sorted(updated_cache.items())]
        new_kmlNames_df = pd.DataFrame(cache_rows, columns=["file", "modified_time"])
        new_kmlNames_df.to_csv(GEO_KML_NAMES_CSV, index=False, encoding="utf-8-sig")
        print()
        print(f"KML cache saved to: {GEO_KML_NAMES_CSV}")

    # 11. Summary
    if new_geo_df.empty:
        if not force_rebuild_geo:
            print()
            print("No new or modified KML files found!")
    else:
        print()
        print(f"Successfully processed/updated {len(new_geo_df)} launches.")
        print()
        print("Candidate Training GEO Samples per Rocket x Sites:")
        dictValueCounts = (new_geo_df["rocket"].value_counts())
        dictSortedValueCounts = sorted(dictValueCounts.items(), key=lambda x: x[1], reverse=True)
        launches_count = dictSortedValueCounts[-1][1]
        for i, (rocket, count) in enumerate(dictSortedValueCounts, 1):
            display_name = (rocket.ljust(12) if rocket.isascii() else rocket.ljust(12 - len(rocket)))
            print(f"{i:2d} {display_name} {count:5d} ({count // launches_count} sites)")
        print()

    return geo_df

# ------------------------------------------------------------
# 7. Build new DataFrame
# 8. Update feature database
# 9. Save feature database
# 10. Save KML cache
# 12. Summary
# ------------------------------------------------------------
def update_iou_featrure_database(new_iou_rows, old_iou_df, iou_feature_file, force_rebuild_iou, updated_cache):
    import pandas as pd

    if new_iou_rows:
        new_iou_df = pd.DataFrame(new_iou_rows)
        first_columns = ["target", "file1", "file2", "site", "rocket1", "rocket2"]
        other_columns = [col for col in new_iou_df.columns if col not in first_columns]
        new_iou_df = new_iou_df[first_columns + other_columns]
    else:
        new_iou_df = pd.DataFrame()

    # 8. Update feature database
    # For modified KMLs:
    #     remove old row first
    #     then add newly parsed row
    if old_iou_df is None:
        iou_df = new_iou_df.copy()
    elif not new_iou_df.empty:
        updated_pairs = set(zip(new_iou_df["file1"].astype(str), new_iou_df["file2"].astype(str)))
        # # Keep old rows whose exact pair was NOT re-parsed.
        old_remaining = old_iou_df[~old_iou_df.apply(lambda row: (str(row["file1"]), str(row["file2"])) in updated_pairs, axis=1)].copy()
        iou_df = pd.concat([old_remaining, new_iou_df], ignore_index=True)
    else:
        iou_df = old_iou_df.copy()

    # Drop duplicated neative samples for one rockets pair per site
    negative = iou_df[iou_df["target"] == 0].copy()
    # negative["negative_key"] = negative.apply(lambda x: (x["site"], *sorted((x["rocket1"], x["rocket2"]))), axis=1)
    negative["rocket_pair"] = negative.apply(lambda x: tuple(sorted((x["rocket1"], x["rocket2"]))), axis=1)
    negative = (negative.sort_values(["site", "rocket_pair", "file1", "file2"]).drop_duplicates(subset=["site", "rocket_pair"], keep="first").drop(columns="rocket_pair"))
    positive = iou_df[iou_df["target"] == 1]
    iou_df = pd.concat([positive, negative], ignore_index=True)

    # Sort by site, file1, file2, target decending
    iou_df = iou_df.sort_values(["site", "file1", "file2", "target"], ascending=[True, True, True, False]).reset_index(drop=True)

    # 9. Save feature database
    if old_iou_df is None or not new_iou_df.empty:
        iou_df.to_csv(iou_feature_file, index=False, encoding="utf-8-sig")
        print(f"\nHistorical launch files: {len(iou_df)}")
        print(f"IoU Feature database saved to: {iou_feature_file}")
    else:
        print("\nIoU Feature database unchanged.")

    if new_iou_rows:
        # 10. Save KML cache
        # Cache contains:
        #     file
        #     modified_time
        # Only successfully parsed new/modified files update
        # their timestamps.
        cache_rows = [{"file": file_name, "modified_time": modified_time} for file_name, modified_time in sorted(updated_cache.items())]
        new_kmlNames_df = pd.DataFrame(cache_rows, columns=["file", "modified_time"])
        new_kmlNames_df.to_csv(IOU_KML_NAMES_CSV, index=False, encoding="utf-8-sig")
        print()
        print(f"KML cache saved to: {IOU_KML_NAMES_CSV}")

    # 11. Summary
    if new_iou_df.empty:
        if not force_rebuild_iou:
            print()
            print("No new or modified KML files found!")
    else:
        print()
        print(f"Successfully processed/updated {len(new_iou_df)} launches.")
        print()
        print("Candidate Training IoU Samples per Rocket1 x Sites:")
        dictValueCounts = (new_iou_df["rocket1"].value_counts())
        dictSortedValueCounts = sorted(dictValueCounts.items(), key=lambda x: x[1], reverse=True)
        launches_count = dictSortedValueCounts[-1][1]
        for i, (rocket, count) in enumerate(dictSortedValueCounts, 1):
            display_name = (rocket.ljust(12) if rocket.isascii() else rocket.ljust(12 - len(rocket)))
            print(f"{i:2d} {display_name} {count:5d} ({count // launches_count:3d} sites)")
        print()
        print("Candidate Training IoU Samples per Rocket2 x Sites:")
        dictValueCounts = (new_iou_df["rocket2"].value_counts())
        dictSortedValueCounts = sorted(dictValueCounts.items(), key=lambda x: x[1], reverse=True)
        launches_count = dictSortedValueCounts[-1][1]
        for i, (rocket, count) in enumerate(dictSortedValueCounts, 1):
            display_name = (rocket.ljust(12) if rocket.isascii() else rocket.ljust(12 - len(rocket)))
            print(f"{i:2d} {display_name} {count:5d} ({count // launches_count:3d} sites)")
        print()
    return iou_df

# ------------------------------------------------------------
# 6. Parse GEO site x rocket Features from GEO target 1/0 feature
# ------------------------------------------------------------
def parse_geo_site_rocket_features(geo_df):
    # features = ["angle_diff", "launch_dz1_km", "launch_dz2_km", "launch_dz3_km", "launch_dz4_km"]
    new_geo_site_rocket_df = geo_df[geo_df["target"] == 1].copy()
    new_geo_site_rocket_df["class"] = new_geo_site_rocket_df["site"] + "_" + new_geo_site_rocket_df["rocket"]
    return new_geo_site_rocket_df

# ------------------------------------------------------------
# 6. Parse GEO Features from new / modified KML files
# ------------------------------------------------------------
def parse_geo_features(to_parse_files, valid_site_rockets, cached_times):
    new_rows = []
    failed = []
    updated_cache = dict(cached_times)

    # Candidate sites
    # Keep the same site rules used by prediction.
    candidate_sites = sorted({site for site, rocket in valid_site_rockets if site != UNKNOWN})
    siteRocketsDict = myConfig.readConfigSiteRocketDict()

    from myModules import myShape
    for number, (kml_path, file_name, current_mtime_str) in enumerate(to_parse_files, start=1):
        try:
            _, mergedGdf, _, _ = myShape.parse_notam_kml_file(kml_path)

            if mergedGdf.empty:
                continue

            print(f"{number:3d}/{len(to_parse_files)}: {file_name} ...")

            history_site = myShape.get_site_from_filename(kml_path, withDetai=True)
            history_rocket = get_rocket_from_filename(kml_path)

            # Generate candidate site × rocket rows
            for candidate_site in candidate_sites:
                # Candidate rockets
                # Use all known historical rockets.
                candidate_rockets = siteRocketsDict.get(candidate_site, ())
                folders = myConfig.readConfig(candidate_site)
                candidate_launch_point = (folders[2].split("+"))
                new_candidate_features_orig = extract_geo_features(candidate_site, candidate_launch_point, mergedGdf, kml_path)

                if not new_candidate_features_orig:
                    continue

                for candidate_rocket in candidate_rockets:
                    if candidate_rocket == "":
                        continue

                    if candidate_site == history_site and candidate_rocket != history_rocket:
                        continue

                    new_candidate_features = new_candidate_features_orig.copy()

                    # Positive only for the real historical site × rocket combination.
                    new_candidate_features["rocket"] = candidate_rocket
                    new_candidate_features["target"] = int(candidate_site == history_site and candidate_rocket == history_rocket)
                    new_rows.append(new_candidate_features)

            updated_cache[file_name] = current_mtime_str

        except Exception as e:
            myExcept.printExceptionTrace()
            failed.append((str(kml_path), str(e)))

    if failed:
        print()
        print(f"WARNING: {len(failed)} files failed.")

        for filename, error in failed[:20]:
            print(filename)
            print("   ", error)

        if len(failed) > 20:
            print(f"... and {len(failed) - 20} more.")

    return new_rows, updated_cache

# ------------------------------------------------------------
# Parse IoU Features historical KML files worker
# ------------------------------------------------------------
def parse_iou_features_worker(args):
    from myModules import myShape

    site, number, parse_files = args
    new_rows = []
    failed = []
    updated_cache = {}
    kml_path1, file_name1, current_mtime_str1 = parse_files[number]

    try:
        _, merged_gdf1, _, _ = myShape.parse_notam_kml_file(kml_path1)

        if merged_gdf1.empty:
            return number, file_name1, new_rows, updated_cache, failed

        rocket1 = get_rocket_from_filename(kml_path1)
        previous_rocket2 = ""

        for kml_path2, file_name2, current_mtime_str2 in parse_files[number + 1:]:
            try:
                rocket2 = get_rocket_from_filename(kml_path2)

                # Keep your existing negative-sample rule
                if rocket1 != rocket2 and rocket2 == previous_rocket2:
                    continue

                _, merged_gdf2, _, _ = myShape.parse_notam_kml_file(kml_path2)

                if merged_gdf2.empty:
                    continue

                new_candidate_features_orig = extract_iou_features(site, merged_gdf1, file_name1, merged_gdf2, file_name2, rocket1, rocket2)

                if not new_candidate_features_orig:
                    continue

                new_candidate_features = new_candidate_features_orig.copy()

                # Positive = same rocket
                new_candidate_features["target"] = int(rocket1 == rocket2)
                new_rows.append(new_candidate_features)
                updated_cache[file_name1] = current_mtime_str1
                previous_rocket2 = rocket2

            except Exception as e:
                failed.append((str(kml_path1), str(kml_path2), str(e)))

            updated_cache[file_name2] = current_mtime_str2
    except Exception as e:
        failed.append((str(kml_path1), "", str(e)))

    return number, file_name1, new_rows, updated_cache, failed

# ------------------------------------------------------------
# 6. Parse IoU Features historical KML files
# ------------------------------------------------------------
def parse_iou_features_full(to_parse_files, cached_times):
    from multiprocessing import Pool, cpu_count
    from myModules import myShape

    new_rows = []
    failed = []
    updated_cache = dict(cached_times)
    processes = max(1, cpu_count() - 1)

    for site, parse_files in to_parse_files.items():
        if len(parse_files) == 0:
            continue

        print()
        print(f"========== {site}: {len(parse_files)} files ==========")

        if len(parse_files) == 1:
            print(f"Skip: Only {parse_files[0][0].name}")
            print(f"========== {site} finished ==========")
            continue

        tasks = [(site, number, parse_files) for number in range(len(parse_files) - 1)]
        pool = Pool(processes=processes)

        try:
            for number, file_name1, rows, cache_update, file_failed in pool.imap_unordered(parse_iou_features_worker, tasks, chunksize=1):
                new_rows.extend(rows)
                updated_cache.update(cache_update)
                failed.extend(file_failed)
                print(f"{number + 1:3d}/{len(parse_files) - 1} Extract IoU Features From File: {file_name1}")

        except KeyboardInterrupt:
            print()
            print("Ctrl+C pressed. Stopping workers...")

            pool.terminate()
            pool.join()

            print("Stopped.")
            return new_rows, updated_cache

        except Exception:
            pool.terminate()
            pool.join()
            raise

        else:
            pool.close()
            pool.join()

        print(f"========== {site} finished ==========")

    if failed:
        print()
        print(f"WARNING: {len(failed)} files failed.")

        for filename1, filename2, error in failed[:20]:
            print(filename1, filename2)
            print("   ", error)

        if len(failed) > 20:
            print(f"... and {len(failed) - 20} more")

    return new_rows, updated_cache

# ------------------------------------------------------------
# 6. Parse IoU Features from new / modified KML files
# ------------------------------------------------------------
def parse_iou_features_append(to_parse_files, cached_times):
    from myModules import myShape

    new_rows = []
    failed = []
    updated_cache = dict(cached_times)
    siteFolders = myConfig.readConfigSitesFolders()

    for site, parse_files in to_parse_files.items():
        if len(parse_files) == 0:
            continue

        to_parse_files_same_site = myConfig.parseFilesFromSite(siteFolders, site)

        print()
        print(f"========== {site}: {len(to_parse_files_same_site)} files ==========")

        if len(to_parse_files_same_site) == 0:
            print(f"Skip: Only {parse_files[0][0].name}")
            print(f"========== {site} finished ==========")
            continue

        for number, (new_kml_path, new_file_name, current_mtime_str1) in enumerate(parse_files):
            _, new_merged_gdf, _, _ = myShape.parse_notam_kml_file(new_kml_path)

            if new_merged_gdf.empty:
                continue

            print(f"{number + 1:3d}/{len(parse_files)} Extract IoU Features From File: {new_file_name}...")

            previous_old_rocket = ""
            new_rocket = get_rocket_from_filename(new_kml_path)

            for old_kml_path in to_parse_files_same_site:
                try:
                    if new_kml_path == old_kml_path:
                        continue

                    old_rocket = get_rocket_from_filename(old_kml_path)

                    if new_rocket != old_rocket and old_rocket == previous_old_rocket:
                        continue

                    _, old_merged_gdf, _, _ = myShape.parse_notam_kml_file(old_kml_path)
                    if old_merged_gdf.empty:
                        continue

                    # print(f"                                       : {old_kml_path.name}...")
                    new_candidate_features_orig = extract_iou_features(site, old_merged_gdf, old_kml_path.name, new_merged_gdf, new_file_name, old_rocket, new_rocket)

                    if not new_candidate_features_orig:
                        continue

                    new_candidate_features = new_candidate_features_orig.copy()

                    # Positive only for the real historical site × rocket combination.
                    new_candidate_features["target"] = int(new_rocket == old_rocket)
                    new_rows.append(new_candidate_features)
                    # updated_cache[old_kml_path.name] = current_mtime_str1
                    previous_old_rocket = old_rocket

                except Exception as e:
                    myExcept.printExceptionTrace()
                    failed.append((str(new_kml_path), str(old_kml_path), str(e)))

            updated_cache[new_file_name] = current_mtime_str1

        if failed:
            print()
            print(f"WARNING: {len(failed)} files failed.")

            for filename1, filename2, error in failed[:20]:
                print(filename1, filename2)
                print("   ", error)

            if len(failed) > 20:
                print(f"... and {len(failed) - 20} more.")

        print(f"========== {site} finished ==========")
    return new_rows, updated_cache

# ------------------------------------------------------------
# 5. Determine which KML files need parsing for GEO feature
# ------------------------------------------------------------
def select_kml_files_geo(kml_files, old_geo_df, cached_times_geo, cache_exists_geo):
    # If feature DB doesn't exist, everything must be parsed.
    # If KML cache doesn't exist, everything must be parsed once
    # so that the cache can be initialized safely.
    from myModules import myShape

    force_rebuild_geo = old_geo_df is None or not cache_exists_geo
    to_parse_files_geo = []
    skipped_unchanged = 0
    skipped_older = 0
    valid_site_rockets = set()

    print()
    for number, kml_path in enumerate(kml_files, start=1):
        if number % 100 == 0:
            print(f"Checked {number}/{len(kml_files)}")

        file_name = kml_path.name

        # Create valid site x rocket set
        site = myShape.get_site_from_filename(kml_path, withDetai=True)
        rocket = get_rocket_from_filename(kml_path)
        valid_site_rockets.add((site, rocket))

        # Current filesystem modification time.
        current_mtime = datetime.fromtimestamp(kml_path.stat().st_mtime)
        current_mtime_str = current_mtime.strftime("%Y-%m-%d %H:%M:%S.%f")

        # First-time build
        if force_rebuild_geo:
            to_parse_files_geo.append((kml_path, file_name, current_mtime_str))

        # File doesn't exist in cache
        cached_time_str = cached_times_geo.get(file_name)

        if cached_time_str is None:
            to_parse_files_geo.append((kml_path, file_name, current_mtime_str))
            continue

        # Compare timestamps
        try:
            cached_mtime_geo = datetime.strptime(cached_time_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # Invalid cached timestamp.
            # Safest behavior: re-parse.
            print(f"WARNING: invalid cached timestamp for {file_name}: {cached_time_str}")
            to_parse_files_geo.append((kml_path, file_name, current_mtime_str))
            continue

        # Current file is NEWER
        if current_mtime > cached_mtime_geo:
            to_parse_files_geo.append((kml_path, file_name, current_mtime_str))
        elif current_mtime == cached_mtime_geo: # Current file is SAME
            skipped_unchanged += 1
        else: # Current file is OLDER
            skipped_older += 1
            print()
            print(f"WARNING: Older KML skipped: {file_name}")
            print(f"    Cached : {cached_time_str}")
            print(f"    Current: {current_mtime_str}")

    print()
    print(f"KML files to parse/update: {len(to_parse_files_geo)}")
    print(f"KML files unchanged      : {skipped_unchanged}")
    print(f"KML files older/skipped  : {skipped_older}")
    return to_parse_files_geo, force_rebuild_geo, valid_site_rockets

# ------------------------------------------------------------
# 5. Determine which KML files need parsing for IoU feature
# ------------------------------------------------------------
def select_kml_files_iou(kml_files, old_iou_df, cached_times_iou, cache_exists_iou):
    # If feature DB doesn't exist, everything must be parsed.
    # If KML cache doesn't exist, everything must be parsed once
    # so that the cache can be initialized safely.
    from myModules import myShape

    force_rebuild_iou = old_iou_df is None or not cache_exists_iou
    to_parse_files_iou = {}
    skipped_unchanged = 0
    skipped_older = 0
    valid_site_rockets = set()

    print()
    for number, kml_path in enumerate(kml_files, start=1):
        if number % 100 == 0:
            print(f"Checked {number}/{len(kml_files)}")

        file_name = kml_path.name

        # Create valid site x rocket set
        site = myShape.get_site_from_filename(kml_path, withDetai=False)
        rocket = get_rocket_from_filename(kml_path)
        valid_site_rockets.add((site, rocket))

        # Current filesystem modification time.
        current_mtime = datetime.fromtimestamp(kml_path.stat().st_mtime)
        current_mtime_str = current_mtime.strftime("%Y-%m-%d %H:%M:%S.%f")

        if site not in to_parse_files_iou:
            to_parse_files_iou[site] = []

        # First-time build
        if force_rebuild_iou:
            to_parse_files_iou[site].append((kml_path, file_name, current_mtime_str))
            continue

        # File doesn't exist in cache
        cached_time_str = cached_times_iou.get(file_name)

        if cached_time_str is None:
            to_parse_files_iou[site].append((kml_path, file_name, current_mtime_str))
            continue

        # Compare timestamps
        try:
            cached_mtime_iou = datetime.strptime(cached_time_str, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # Invalid cached timestamp.
            # Safest behavior: re-parse.
            print(f"WARNING: invalid cached timestamp for {file_name}: {cached_time_str}")
            to_parse_files_iou[site].append((kml_path, file_name, current_mtime_str))
            continue

        # Current file is NEWER
        if current_mtime > cached_mtime_iou:
            to_parse_files_iou[site].append((kml_path, file_name, current_mtime_str))
        elif current_mtime == cached_mtime_iou: # Current file is SAME
            skipped_unchanged += 1
        else: # Current file is OLDER
            skipped_older += 1
            print()
            print(f"WARNING: Older KML skipped: {file_name}")
            print(f"    Cached : {cached_time_str}")
            print(f"    Current: {current_mtime_str}")

    print()
    print(f"KML files to parse/update: {sum(len(v) for v in to_parse_files_iou.values())}")
    print(f"KML files unchanged      : {skipped_unchanged}")
    print(f"KML files older/skipped  : {skipped_older}")
    return to_parse_files_iou, force_rebuild_iou, valid_site_rockets

# ------------------------------------------------------------
# 4. Build cache:
#     filename -> cached modified_time
# ------------------------------------------------------------
def build_kml_cache_times(kmlNames_df):
    cached_times = {}

    if (kmlNames_df is not None and not kmlNames_df.empty and "file" in kmlNames_df.columns):
        if "modified_time" in kmlNames_df.columns:
            import pandas as pd
            for _, row in kmlNames_df.iterrows():
                file_name = str(row["file"])

                if pd.isna(row["modified_time"]):
                    continue

                cached_times[file_name] = str(row["modified_time"])
        else:
            oldest_time = "1970-01-01 00:00:00"

            for file_name in kmlNames_df["file"].dropna().astype(str):
                cached_times[file_name] = oldest_time
    return cached_times

# ------------------------------------------------------------
# 3. Find eligible KML files
# ------------------------------------------------------------
def find_eligibale_kml_files(history_dir):
    kml_files = []

    for kml_path in sorted(history_dir.rglob("*.kml")):
        if "raws" in kml_path.parts:
            continue

        if "old" in kml_path.parts:
            continue

        if "90.其他" in kml_path.parts:
            continue

        if "99.卫星发射中心" in kml_path.parts:
            continue

        if "old" in kml_path.name.lower():
            print(f"Invalid filename: {kml_path}")
            continue

        kml_files.append(kml_path)

    print()
    print(f"Found {len(kml_files)} KML files.")
    return kml_files

# ------------------------------------------------------------
# 2. Read KML cache
# ------------------------------------------------------------
def read_kml_cache(kml_names_file):
    cache_exists = kml_names_file.is_file()
    kmlNames_df = None

    if cache_exists:
        import pandas as pd
        kmlNames_df = pd.read_csv(kml_names_file)

        if "file" not in kmlNames_df.columns:
            print(f"WARNING: {kml_names_file} does not contain 'file' column.")
            kmlNames_df = pd.DataFrame()

        print()
        print(f"KML cache read from: {kml_names_file}")

        if "file" in kmlNames_df.columns:
            print(f"Cached KML files: {len(kmlNames_df)}")
        else:
            print("Cached KML files: 0")

    return kmlNames_df, cache_exists

# ============================================================
# 1. Read existing feature database GEO
# ============================================================
def read_featrure_database_geo(geo_feature_File, isRocketRocket=False):
    old_geo_df = None

    if geo_feature_File.is_file() and geo_feature_File.stat().st_size > 10000:
        import pandas as pd
        print()
        print(f"GEO Feature database read from: {geo_feature_File}")
        old_geo_df = pd.read_csv(geo_feature_File)
        print(f"Historical GEO samples: {len(old_geo_df)}")

    return old_geo_df

# ============================================================
# 1. Read existing feature database IoU
# ============================================================
def read_featrure_database_iou(iou_feature_file):
    old_iou_df = None

    if iou_feature_file.is_file() and iou_feature_file.stat().st_size > 10000:
        import pandas as pd
        print()
        print(f"IoU Feature database read from: {iou_feature_file}")
        old_iou_df = pd.read_csv(iou_feature_file)
        print(f"Historical IoU samples: {len(old_iou_df)}")

    return old_iou_df

# ============================================================
# Build feature database
# ============================================================
def build_feature_database(history_dir):
    """
    Incrementally build the historical feature database.
    KML cache:
        kml_names.csv
            file
            modified_time
    Rules:
        - New KML file:
            Parse it.
        - Current KML modified time > cached modified time:
            Re-parse and replace the old feature row.
        - Current KML modified time == cached modified time:
            Skip it.
        - Current KML modified time < cached modified time:
            Skip it and show a warning.
            This protects against accidentally copying an older KML
            over a newer historical version.
    One launch = one row.
    """

    kml_files = find_eligibale_kml_files(history_dir)

    # Build IoU features for target binary 1/0
    kml_names_df_iou, cache_exists_iou = read_kml_cache(IOU_KML_NAMES_CSV)
    cached_times_iou = build_kml_cache_times(kml_names_df_iou)
    old_iou_df = read_featrure_database_iou(IOU_FEATURE_CSV)
    to_parse_files_iou, force_rebuild_iou, valid_site_rockets = select_kml_files_iou(kml_files, old_iou_df, cached_times_iou, cache_exists_iou)
    new_iou_rows, updated_cache = parse_iou_features_full(to_parse_files_iou, cached_times_iou) if force_rebuild_iou else parse_iou_features_append(to_parse_files_iou, cached_times_iou)
    iou_df = update_iou_featrure_database(new_iou_rows, old_iou_df, IOU_FEATURE_CSV, force_rebuild_iou, updated_cache)

    # Build GEO features for target binary 1/0
    kml_names_df_geo, cache_exists_geo = read_kml_cache(GEO_KML_NAMES_CSV)
    cached_times_geo = build_kml_cache_times(kml_names_df_geo)
    old_geo_df = read_featrure_database_geo(GEO_FEATURE_CSV)
    to_parse_files_geo, force_rebuild_geo, valid_site_rockets = select_kml_files_geo(kml_files, old_geo_df, cached_times_geo, cache_exists_geo)
    new_geo_rows, updated_cache = parse_geo_features(to_parse_files_geo, valid_site_rockets, cached_times_geo)
    geo_df = update_geo_featrure_database(new_geo_rows, old_geo_df, GEO_FEATURE_CSV, force_rebuild_geo, updated_cache)

    # Build GEO features for target classes site x rocket
    geo_site_rocket_df = parse_geo_site_rocket_features(geo_df)

    return iou_df, new_iou_rows, geo_df, new_geo_rows, geo_site_rocket_df

# ============================================================
# Is Route Angle Compatible
# ============================================================
def isRouteAngleCompatible(routeAngle, candidateAngles):
    return any((routeAngle <= 90 and candidateAngle <= 90) or (routeAngle >= 90 and candidateAngle >= 90) for candidateAngle in candidateAngles)

# ============================================================
# Compare Old Method and New Method
# ============================================================
def compareOldNew(old_features, new_features):
    old_features = {k: old_features[k] for k in sorted(old_features)}
    new_features = {k: new_features[k] for k in sorted(new_features)}
    for (oldKey, oldValue), (newKey, newValue) in zip(old_features.items(), new_features.items()):
        if oldKey != newKey and oldValue != newValue:
            print("=== COMPARE OLD/NEW METHOD ===")
            print(f"{oldKey=}, {oldValue}")
            print(f"{newKey=}, {newValue}")
            input("Press ENTER to continue ...")

# ============================================================
# Check Route Direction if Compatible
# ============================================================
def route_direction_is_compatible(candidate_launch_point, kml_path):
    from shapely import Point
    if not isinstance(candidate_launch_point, Point):
        candidate_launch_point = Point(candidate_launch_point)

    from myModules import myShape
    _, _, launch_point, last_point = myShape.parse_notam_kml_file(kml_path)
    route_angle = myMath.launch_azimuth(launch_point.x, launch_point.y, last_point.x, last_point.y)
    candidate_route_angle = myMath.launch_azimuth(candidate_launch_point.x, candidate_launch_point.y, last_point.x, last_point.y)
    print(f"{route_angle=}°, {candidate_route_angle=}°")
    return (route_angle <= 90 and candidate_route_angle <= 90) or (route_angle >= 0 and candidate_route_angle >= 0)

# ============================================================
# Prepare ML GEO Data
# ============================================================
def prepare_geo_features(df, isSiteRocket=False, debug=False):
    """
    Separate features X and rocket labels y.
    """

    if isSiteRocket:
        feature_columns = ["angle_diff", "launch_dz1_km", "launch_dz2_km", "launch_dz3_km", "launch_dz4_km"]
        numeric_features = feature_columns
        categorical_features = []
        X = df[feature_columns].copy()
        y = df["class"].copy()
    else:
        ignored_columns = ["target", "file"]
        feature_columns = [column for column in df.columns if column not in ignored_columns]
        numeric_features = [column for column in df.columns if column not in ["target", "file", "site", "rocket"]]
        categorical_features = ["site", "rocket"]
        X = df[feature_columns].copy()
        y = df["target"].copy()

    if debug:
        print("\nBasic Features:")
        print("=============================")
        print("Basic Features:", len(feature_columns))
        print("Basic numerics:", len(numeric_features))
        print("Basic Categoricals:", len(categorical_features))

    return X, y, feature_columns, numeric_features, categorical_features

# ============================================================
# Prepare ML IoU Data
# ============================================================
def prepare_iou_features(df, debug=False):
    """
    Separate features X and rocket labels y.
    """

    ignored_columns = ["target", "file1", "file2"]
    feature_columns = [column for column in df.columns if column not in ignored_columns]
    numeric_features = [column for column in df.columns if column not in ["target", "file1", "file2", "site", "rocket1", "rocket2"]]
    categorical_features = ["site", "rocket1", "rocket2"]

    if debug:
        print("\nBasic Features:")
        print("=============================")
        print("Basic Features:", len(feature_columns))
        print("Basic numerics:", len(numeric_features))
        print("Basic Categoricals:", len(categorical_features))

    X = df[feature_columns].copy()
    y = df["target"].copy()
    return X, y, feature_columns, numeric_features, categorical_features

# =============================================================
# Split all files for production
# =============================================================
def chronological_split(df, isIou=False, trainRate=1.00, debug=False):
    """
    Use older launches for training and newer launches for testing.
    This is closer to your real-world use case.
    """
    import pandas as pd

    test_fraction = 1.00 - trainRate
    df = df.copy()

    # Try to recover date/time from filename.
    # We first try to extract the date from the filename.
    if isIou:
        df["_filename"] = df["file1"].apply(lambda x: Path(x).name)
    else:
        df["_filename"] = df["file"].apply(lambda x: Path(x).name)

    # Find YYYY年MM月DD日
    dates = df["_filename"].str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
    df["_date"] = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")

    # If date extraction failed, use filename order as a fallback.
    if df["_date"].notna().sum() < len(df) * MIN_DATE_COVERAGE:
        print("Warning: many dates could not be extracted.")
        df = df.sort_values("_filename")
    else:
        df = df.sort_values("_date")

    n_test = int(len(df) * test_fraction)

    if n_test > 0:
        train_df = df.iloc[:-n_test].copy()
        test_df = df.iloc[-n_test:].copy()
        test_df = test_df.drop(columns=["_filename", "_date"])
    else:
        train_df = df.copy()
        test_df = df.iloc[0:0].copy()

    train_df = train_df.drop(columns=["_filename", "_date"])
    return train_df, test_df

# =============================================================
# split class by ratio for train or prod
# =============================================================
def split_class_by_ratio(group, trainRate=0.80):
    """
    Chronological split for one class.
    Normal evaluation:
        - Older launches -> training
        - Newer launches -> testing
        - Classes with fewer than 3 samples remain entirely in training.
        - At least 2 samples are kept in training.
    """

    n = len(group)

    # Normal train/test evaluation
    if n < 3:
        return group.copy(), group.iloc[0:0].copy()

    test_fraction = 1.00 - trainRate
    test_count = max(1, floor(n * test_fraction + 0.5))
    # test_count = max(1, round(n * test_fraction))

    # Always leave at least 2 training samples
    test_count = min(test_count, n - 2)
    train_count = n - test_count
    return (group.iloc[:train_count].copy(), group.iloc[train_count:].copy())

# =============================================================
# Split chronologically within each rocket: 
#   oldest 80% for training, newest 20% for test
# =============================================================
def chronological_split_per_rocket(df, trainRate=0.80, debug=False):
    """
    Split chronologically within each rocket.
    For each rocket:
        older launches -> training
        newer launches -> testing
    A rocket with only one launch is kept in training only.
    """
    import pandas as pd

    df = df.copy()

    # Recover date/time from filename
    df["_filename"] = df["file"].apply(lambda x: Path(x).name)
    dates = df["_filename"].str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
    df["_date"] = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")

    train_parts = []
    test_parts = []

    for rocket, group in df.groupby("rocket"):
        group = group.sort_values("_date")
        train_group, test_group = split_class_by_ratio(group, trainRate=trainRate)
        train_parts.append(train_group)
        test_parts.append(test_group)

    train_df = pd.concat(train_parts, ignore_index=True)
    test_df = pd.concat(test_parts, ignore_index=True)

    # Optional randomization of rows AFTER the chronological split.
    # This does NOT change which launches belong to train/test.
    # if split_random_state > 0:
    #     train_df = train_df.sample(frac=1, random_state=split_random_state).reset_index(drop=True)
    #     test_df = test_df.sample(frac=1, random_state=split_random_state).reset_index(drop=True)

    # Remove temporary columns
    train_df = train_df.drop(columns=["_filename", "_date"])
    test_df = test_df.drop(columns=["_filename", "_date"])

    if debug:
        print()
        print("=" * 60)
        print("PER-ROCKET TRAIN / TEST SPLIT CHECK")
        print("=" * 60)
        print(f"Training: {len(train_df)}")
        print(f"Testing : {len(test_df)}")
        print()
        print("Training rocket counts:")
        print(train_df["rocket"].value_counts().sort_index().to_string())
        print()
        print("Testing rocket counts:")
        print(test_df["rocket"].value_counts().sort_index().to_string())
        print()
        print("Rocket distribution:")

        split_check = pd.concat([
            train_df["rocket"].value_counts().rename("train"),
            test_df["rocket"].value_counts().rename("test")
        ], axis=1).fillna(0).astype(int)

        split_check["total"] = (split_check["train"] + split_check["test"])
        split_check["test_%"] = (split_check["test"] / split_check["total"] * 100).round(1)
        print(split_check.sort_values("total", ascending=False).to_string())
        print()
        print("Training date range:")
        print(train_df["file"].min())
        print(train_df["file"].max())
        print()
        print("Testing date range:")
        print(test_df["file"].min())
        print(test_df["file"].max())

        print("*********************** SPLITTER TRAIN:", len(train_df))
        print("***********************  SPLITTER TEST:", len(test_df))
        rate = int(100 * (len(train_df) / (len(test_df) + len(train_df))))
        print(f"***********************    TRAIN/TOTAL: {rate}%")
    return train_df, test_df

# =============================================================
# Split chronologically within each site: 
#   oldest 80% for training, newest 20% for test
# =============================================================
def chronological_split_per_site(df, trainRate=0.80, debug=False):
    """
    Split chronologically within each site.
    For each site:
        older launches -> training
        newer launches -> testing
    A site with too few launches is handled by
    split_class_by_ratio().
    The chronological split is performed independently
    for each site.
    """
    import pandas as pd

    df = df.copy()

    # Recover date/time from filename
    df["_filename"] = df["file"].apply(lambda x: Path(x).name)
    dates = df["_filename"].str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
    df["_date"] = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")

    train_parts = []
    test_parts = []

    for site, group in df.groupby("site"):
        group = group.sort_values("_date")
        train_group, test_group = split_class_by_ratio(group, trainRate=trainRate)
        train_parts.append(train_group)
        test_parts.append(test_group)

    train_df = pd.concat(train_parts, ignore_index=True)
    test_df = pd.concat(test_parts, ignore_index=True)

    # Remove temporary columns
    train_df = train_df.drop(columns=["_filename", "_date"])
    test_df = test_df.drop(columns=["_filename", "_date"])

    if debug:
        print()
        print("=" * 60)
        print("PER-SITE TRAIN / TEST SPLIT CHECK")
        print("=" * 60)
        print(f"Training: {len(train_df)}")
        print(f"Testing : {len(test_df)}")
        print()
        print("Training site counts:")
        print(train_df["site"].value_counts().sort_index().to_string())
        print()
        print("Testing site counts:")
        print(test_df["site"].value_counts().sort_index().to_string())
        print()
        print("Site distribution:")
        split_check = pd.concat([
            train_df["site"].value_counts().rename("train"),
            test_df["site"].value_counts().rename("test")
        ], axis=1).fillna(0).astype(int)

        split_check["total"] = (split_check["train"] + split_check["test"])
        split_check["test_%"] = (split_check["test"] / split_check["total"] * 100).round(1)
        print(split_check.sort_values("total", ascending=False).to_string())
        print()
        print("Training date range:")
        print(train_df["file"].min())
        print(train_df["file"].max())
        print()
        print("Testing date range:")
        print(test_df["file"].min())
        print(test_df["file"].max())

        print("*********************** SPLITTER TRAIN:", len(train_df))
        print("***********************  SPLITTER TEST:", len(test_df))
        rate = int(100 * (len(train_df) / (len(test_df) + len(train_df))))
        print(f"***********************    TRAIN/TOTAL: {rate}%")
    return train_df, test_df

# =============================================================
# Split chronologically within each (site, rocket) combination: 
#   oldest 80% for training, newest 20% for test
# =============================================================
def chronological_split_per_site_rocket(df, isIou=False, trainRate=0.80, debug=False):
    """
    Split chronologically within each (site, rocket) combination.
    For each site + rocket combination:
        older launches -> training
        newer launches -> testing
    A site + rocket combination with only one launch
    is kept in training only.
    """
    import pandas as pd

    df = df.copy()
    train_parts = []
    test_parts = []

    if isIou:
        # Recover date/time from filename
        df["_filename1"] = df["file1"].apply(lambda x: Path(x).name)
        dates = df["_filename1"].str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
        df["_date1"] = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")

        df["_filename2"] = df["file2"].apply(lambda x: Path(x).name)
        dates = df["_filename2"].str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
        df["_date2"] = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")

        for (site, rocket1), group in df.groupby(["site", "rocket1"]):
            group = group.sort_values("_date1")
            train_group, test_group = split_class_by_ratio(group, trainRate=trainRate)
            test_files = set(test_group["_filename1"]) | set(test_group["_filename2"])
            train_group = train_group[~train_group["_filename1"].isin(test_files) & ~train_group["_filename2"].isin(test_files)]
            train_parts.append(train_group)
            test_parts.append(test_group)
    else:
        # Recover date/time from filename
        df["_filename"] = df["file"].apply(lambda x: Path(x).name)
        dates = df["_filename"].str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
        df["_date"] = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")

        for (site, rocket), group in df.groupby(["site", "rocket"]):
            group = group.sort_values("_date")
            train_group, test_group = split_class_by_ratio(group, trainRate=trainRate)
            train_parts.append(train_group)
            test_parts.append(test_group)

    train_df = pd.concat(train_parts, ignore_index=True)
    test_df = pd.concat(test_parts, ignore_index=True)

    # Remove temporary columns
    if isIou:
        train_df = train_df.drop(columns=["_filename1", "_filename2", "_date1", "_date2"])
        test_df = test_df.drop(columns=["_filename1", "_filename2", "_date1", "_date2"])
    else:
        train_df = train_df.drop(columns=["_filename", "_date"])
        test_df = test_df.drop(columns=["_filename", "_date"])

    if debug:
        print()
        print("=" * 60)
        print("PER-SITE + ROCKET TRAIN / TEST SPLIT CHECK")
        print("=" * 60)
        print(f"Training: {len(train_df)}")
        print(f"Testing : {len(test_df)}")
        print()
        print("Training rocket counts:")
        print(train_df["rocket"].value_counts().sort_index().to_string())
        print()
        print("Testing rocket counts:")
        print(test_df["rocket"].value_counts().sort_index().to_string())
        print()
        print("Testing site + rocket counts:")
        print(test_df.groupby(["site", "rocket"]).size().sort_values(ascending=False).to_string())
        print()
        print("Site + rocket distribution:")

        split_check = pd.concat([
            train_df.groupby(["site", "rocket"]).size().rename("train"),
            test_df.groupby(["site", "rocket"]).size().rename("test")
        ], axis=1).fillna(0).astype(int)

        split_check["total"] = (split_check["train"] + split_check["test"])
        split_check["test_%"] = (split_check["test"] / split_check["total"] * 100).round(1)
        print(split_check.sort_values(["site", "total"], ascending=[True, False]).to_string())
        print()
        print("Training date range:")
        print(train_df["file"].min())
        print(train_df["file"].max())
        print()
        print("Testing date range:")
        print(test_df["file"].min())
        print(test_df["file"].max())

        print("*********************** SPLITTER TRAIN:", len(train_df))
        print("***********************  SPLITTER TEST:", len(test_df))
        rate = int(100 * (len(train_df) / (len(test_df) + len(train_df))))
        print(f"***********************    TRAIN/TOTAL: {rate}%")
    return train_df, test_df

# ============================================================
# Build Random Forest model
# ============================================================
def build_model_rf(df, isIou=False, isSiteRocket=False, debug=False):
    """
    Train Random Forest.
    """
    print(f"\nTraining RF Model with {'IoU' if isIou else 'GEO'} features and Target {'CLASSES' if isSiteRocket else 'BINARY'} ...")

    if isIou:
        X, y, feature_columns, numeric_features, categorical_features = prepare_iou_features(df)
    else:
        if isSiteRocket:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df, isSiteRocket=True)
        else:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df)

    # Preprocessing
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True))
    ])

    if categorical_features:
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent", add_indicator=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ])
    else:
        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
        ])

    # Random Forest
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=500, 
            msx_depth=None,
            min_samples_leaf=1,
            max_features="sqrt",
            max_samples=None,
            class_weight="balanced", 
            n_jobs=-1, 
            oob_score=False, 
            random_state=MODEL_RANDOM_STATE))
    ])

    # Train all samples
    model.fit(X, y)
    return model, feature_columns

# ============================================================
# Build Extra Trees
# ============================================================
def build_model_et(df, isIou=False, isSiteRocket=False, debug=False):
    """
    Train Extra Tress.
    """
    print(f"\nTraining ET Model with {'IoU' if isIou else 'GEO'} features and Target {'CLASSES' if isSiteRocket else 'BINARY'} ...")

    if isIou:
        X, y, feature_columns, numeric_features, categorical_features = prepare_iou_features(df)
    else:
        if isSiteRocket:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df, isSiteRocket=True)
        else:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df)

    # Preprocessing
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import ExtraTreesClassifier

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True))
    ])

    if categorical_features:
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent", add_indicator=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ])
    else:
        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
        ])

    # Random Forest
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", ExtraTreesClassifier(
            n_estimators=500,
            max_depth=None,
            min_samples_leaf=1,
            max_features="sqrt",
            class_weight="balanced", 
            n_jobs=-1, 
            random_state=MODEL_RANDOM_STATE))
    ])

    # Train all samples
    model.fit(X, y)
    return model, feature_columns

# ============================================================
# Build Hist Gradient Boosting
# ============================================================
def build_model_hgb(df, isIou=False, isSiteRocket=False, debug=False):
    """
    Build HGB.
    """
    print(f"\nTraining HGB Model with {'IoU' if isIou else 'GEO'} features and Target {'CLASSES' if isSiteRocket else 'BINARY'} ...")

    if isIou:
        X, y, feature_columns, numeric_features, categorical_features = prepare_iou_features(df)
    else:
        if isSiteRocket:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df, isSiteRocket=True)
        else:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df)

    # Preprocessing
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import HistGradientBoostingClassifier

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True))
    ])

    if categorical_features:
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent", add_indicator=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ])
    else:
        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
        ])

    # ------------------------------------------------------------
    # Hist Gradient Boosting
    # ------------------------------------------------------------
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", HistGradientBoostingClassifier(
            max_iter=200, 
            learning_rate=0.05, 
            max_leaf_nodes=15, 
            max_depth=None,
            min_samples_leaf=20,
            l2_regularization=1, 
            random_state=MODEL_RANDOM_STATE,))
    ])

    # Train all samples
    model.fit(X, y)
    return model, feature_columns

# ============================================================
# Build Gradient Boosting
# ============================================================
def build_model_gb(df, isIou=False, isSiteRocket=False, subsample=1.0, debug=False):
    """
    Build GB.
    """

    print(f"\nTraining GB Model with {'IoU' if isIou else 'GEO'} features and Target {'CLASSES' if isSiteRocket else 'BINARY'} ...")

    if isIou:
        X, y, feature_columns, numeric_features, categorical_features = prepare_iou_features(df)
    else:
        if isSiteRocket:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df, isSiteRocket=True)
        else:
            X, y, feature_columns, numeric_features, categorical_features = prepare_geo_features(df)

    # Preprocessing
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import GradientBoostingClassifier

    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True))
    ])

    if categorical_features:
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent", add_indicator=True)),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ])
    else:
        preprocessor = ColumnTransformer([
            ("num", numeric_transformer, numeric_features),
        ])

    # ------------------------------------------------------------
    # Gradient Boosting
    # ------------------------------------------------------------
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", GradientBoostingClassifier(
            n_estimators=200, 
            learning_rate=0.05, 
            max_depth=2, 
            subsample=subsample, 
            random_state=MODEL_RANDOM_STATE,))
    ])

    # Train all samples
    model.fit(X, y)
    return model, feature_columns

# ============================================================
# Check production Model features
# ============================================================
def check_prod_model(prod_df, feature_columns, model, trainRate=1.00, debug=False):
    """
    Sanity-check a production model and its production training data.
    This does NOT calculate accuracy because prod_df was used to train
    the production model.
    """

    if not debug:
        return True

    print()
    print("=" * 70)
    print(f"PRODUCTION MODEL CHECK")
    print("=" * 70)

    # Basic information
    total_count = len(prod_df)
    print(f"Production launches : {total_count:,}")

    if trainRate is not None:
        print(f"Requested trainRate : {trainRate:.1%}")

    print(f"Feature count       : {len(feature_columns):,}")
    print(f"Model classes       : {len(model.classes_):,}")

    if total_count > 0:
        print()
        print("Rocket classes:")
        print(prod_df["rocket"].value_counts().sort_index().to_string())

    # Site information
    if "site" in prod_df.columns:
        print()
        print("Site counts:")
        print(prod_df["site"].value_counts().sort_index().to_string())

    # Site + Rocket information
    if "site" in prod_df.columns and "rocket" in prod_df.columns:
        print()
        print("Site + Rocket counts:")
        site_rocket_counts = (prod_df.groupby(["site", "rocket"]).size().sort_values(ascending=False))
        print(site_rocket_counts.to_string())

    # Date range
    if "file" in prod_df.columns:
        import pandas as pd
        filenames = prod_df["file"].map(lambda x: Path(x).name)
        dates = filenames.str.extract(r"(\d{4})年(\d{1,2})月(\d{1,2})日")
        parsed_dates = pd.to_datetime(dates[0] + "-" + dates[1] + "-" + dates[2], errors="coerce")
        valid_dates = parsed_dates.dropna()

        print()
        print("Date range:")

        if len(valid_dates) > 0:
            print(f"Oldest: {valid_dates.min().date()}")
            print(f"Newest: {valid_dates.max().date()}")
            print(f"Valid dates: {len(valid_dates)}/{len(parsed_dates)}")
        else:
            print("No valid dates found.")

    # Model classes vs production data
    prod_rockets = set(prod_df["rocket"].dropna().unique())
    model_rockets = set(model.classes_)
    missing_from_model = sorted(prod_rockets - model_rockets)
    extra_in_model = sorted(model_rockets - prod_rockets)

    print()
    print("Model class check:")

    if not missing_from_model:
        print("All production rockets are present in model.classes_.")
    else:
        print("WARNING: Rockets missing from model:")
        print(missing_from_model)

    if extra_in_model:
        print()
        print("Model classes with no production samples:")
        print(extra_in_model)

    # Site values
    print()
    print("Model site values:")

    if hasattr(model, "site_values_"):
        print(model.site_values_)
    else:
        print("WARNING: model.site_values_ is missing.")

    # Feature sanity check
    print()
    print("Feature check:")

    missing_features = [column for column in feature_columns if column not in prod_df.columns]

    if missing_features:
        print("WARNING: Missing production features:")
        print(missing_features)
    else:
        print("All model features are present in production data.")

    # Summary
    print()
    print("-" * 70)
    print("Production model check completed.")
    print("Note: accuracy is NOT calculated because prod_df was used for training.")
    print("-" * 70)

    return True

# ============================================================
# show top k accuracy
# ============================================================
def show_top_k_accuracy(model, test_df, debug=False):
    """
    Show Top-1 / Top-2 / Top-3 / Top-5 accuracy for Method #3.

    Each historical launch (`file`) is one evaluation case.
    Candidate site × rocket rows belonging to the same launch
    are ranked by P(target=1).
    """
    import numpy as np
    results = {}

    X_test = test_df.drop(columns=["target"])
    y_test = test_df["target"]

    if debug:
        print("\n*****DEBUG*****")
        print("X_test:", X_test.shape)
        print("y_test:", len(y_test))
        print("test files:", test_df["file"].nunique())
        print("target counts:")
        print(y_test.value_counts())

    probabilities = model.predict_proba(X_test)
    classes = model.classes_

    # Probability of target=1
    positive_index = np.where(classes == 1)[0][0]
    probabilities = probabilities[:, positive_index]

    test_result = test_df[["file", "target"]].copy()
    test_result["probability"] = probabilities

    print()
    print("=" * 70)
    print("TOP-K ACCURACY")
    print("=" * 70)

    for k in [1, 2, 3, 5]:
        correct = 0

        for file, group in test_result.groupby("file"):
            ranked = group.sort_values(
                "probability",
                ascending=False
            )

            top_k = ranked.head(k)

            if top_k["target"].eq(1).any():
                correct += 1

        total = test_result["file"].nunique()
        accuracy = correct / total

        results[k] = accuracy

        print(
            f"Top-{k}: {correct:3d} / {total:3d} "
            f"({accuracy:.2%})"
        )

    return results

# ============================================================
# Evaluate model
# ============================================================
def evaluate_model(model, train_df, test_df, feature_columns, debug=False):
    """
    Evaluate on launches that were not used for training.
    """
    import numpy as np
    X_test = test_df.copy()
    X_test = X_test.reindex(columns=feature_columns, fill_value=0)
    y_test = test_df["target"]
    y_train = train_df["target"]

    print(X_test[["site", "rocket", "angle_diff"]].to_string(index=False))

    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    probabilities = model.predict_proba(X_test)
    classes = model.classes_
    results = show_top_k_accuracy(model, test_df)

    if debug:
        import pandas as pd
        check_df = test_df[["rocket", "file"]].copy()
        check_df["feature_hash"] = pd.util.hash_pandas_object(check_df, index=False)
        print()
        print("=" * 70)
        print(f"DUPLICATE TEST FEATURE ROWS")
        print("=" * 70)
        print(f"Test launches         : {len(check_df)}")
        print(f"Unique feature vectors: {check_df["feature_hash"].nunique()}")
        print(f"Duplicate rows        : {check_df["feature_hash"].duplicated(keep=False).sum()}")
        duplicates = check_df[check_df["feature_hash"].duplicated(keep=False)].sort_values("feature_hash")
        if not duplicates.empty:
            print()
            for feature_has, group in duplicates.groupby("feature_has"):
                print(f"Feature has: {feature_has}")
                print(group[["rocket", "file"]].to_string(index=False))
                print()

        print()
        print("=" * 70)
        print(f"MISCLASSIFIED TEST LAUNCHES - TOP 3 PROBABILITIES")
        print("=" * 70)
        for actual, predicted, probs in zip(y_test, predictions, probabilities):
            if actual == predicted:
                continue
            top_indices = np.argsort(probs)[::-1][:3]
            print(f"Actual: {actual}")
            print(f"Predicted: {predicted}")
            for rank, index in enumerate(top_indices, 1):
                print(f"  {rank}, {classes[index]:12s}, {probs[index]:.3f}")

        print()
        print("=" * 70)
        print(f"MISCLASSIFIED TEST LAUNCHES")
        print("=" * 70)
        for actual, predicted in zip(y_test, predictions):
            if actual != predicted:
                print(f"{actual:12s} -> {predicted:12s}")

        print()
        print("=" * 60)
        print(f"MODEL TEST RESULT")
        print("=" * 60)
        print(f"Accuracy:{accuracy:.2%}")

    labels = sorted(set(y_train) | set(y_test) | set(predictions))
    report = classification_report(y_test, predictions, labels=labels, target_names=["negative", "positive"], zero_division=0, output_dict=True)

    if debug:
        print()
        print(f"Total Classification report")
        print(f"{report=}")

    # Plot Total Confusion matrix
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])

    if debug:
        print(f"\nTotal Confusion matrix")
        print(matrix)

    return results

# ============================================================
# Report Method3 Ranking
# ============================================================
def report_train_test_ranking(model, test_df, isIou=False, isHgb=False, trainRate=0.80):
    if isIou:
        feature_columns = ["iou1", "iou2", "iou3", "iou4", "site", "rocket1", "rocket2"]
    else:
        feature_columns = ["angle_diff", "launch_dz1_km", "launch_dz2_km", "launch_dz3_km", "launch_dz4_km", "site", "rocket"]
    
    candidate_df = test_df.copy()
    print("\nCalculating candidate probabilities...")
    print(f"Candidate rows: {len(candidate_df)}")
    print(f"Candidate columns: {len(candidate_df.columns)}")

    import time
    t0 = time.time()

    probabilities = model.predict_proba(candidate_df[feature_columns])
    
    positive_index = list(model.classes_).index(1)
    candidate_df["probability"] = probabilities[:, positive_index]
    print(f"predict_proba finished: {time.time() - t0:.2f} seconds")

    # Rank candidates within each historical launch
    results = []

    if isIou:
        for file1, group in candidate_df.groupby("file1", sort=False):
            group = group.sort_values("probability", ascending=False).reset_index(drop=True)
            group["prediction_rank"] = group.index + 1
            actual_rows = group[group["target"] == 1]

            if len(actual_rows) == 0:
                continue

            actual = actual_rows.iloc[0]

            results.append({
                "file": file1,
                "actual_site": actual["site"],
                "actual_rocket": actual["rocket1"],
                "predicted_site": group.iloc[0]["site"],
                "predicted_rocket": group.iloc[0]["rocket1"],
                "prediction_rank": int(actual["prediction_rank"]),
                "actual_probability": float(actual["probability"]),
                "actual_iou1": float(actual["iou1"]),
                "actual_iou2": float(actual["iou2"]),
                "actual_iou3": float(actual["iou3"]),
                "actual_iou4": float(actual["iou4"]),
                "top5": "|".join(f"{row['site']} × {row['rocket1']}:({row['probability']:.3f}, IoU={row['iou1']:.2%})" for _, row in group.head(5).iterrows())
            })
    else:
        for file, group in candidate_df.groupby("file", sort=False):
            group = group.sort_values("probability", ascending=False).reset_index(drop=True)
            group["rank"] = group.index + 1
            actual_rows = group[group["target"] == 1]

            if len(actual_rows) == 0:
                continue

            actual = actual_rows.iloc[0]
            results.append({
                "file": file,
                "actual_site": actual["site"],
                "actual_rocket": actual["rocket"],
                "predicted_site": group.iloc[0]["site"],
                "predicted_rocket": group.iloc[0]["rocket"],
                "combo_rank": int(actual["rank"]),
                "actual_probability": float(actual["probability"]),
                "top5": "|".join(f"{row['site']} × {row['rocket']}:({row['probability']:.3f})" for _, row in group.head(5).iterrows())
            })

    import pandas as pd
    result_df = pd.DataFrame(results)

    # Print ranking
    matched = ((result_df["predicted_site"] == result_df["actual_site"]) & (result_df["predicted_rocket"] == result_df["actual_rocket"]))
    matchedCount = matched.sum()
    unmatchedCount = (~matched).sum()
    trainTitle = f"(split {int(trainRate * 100)}% train / {100- int(trainRate * 100)}% test by split for {SPLIT_MODE_SITE_ROCKET})"
    print()
    print(f"\n=== TRAIN RANKING with Model {'HGB' if isHgb else 'RF'} features {'IoU' if isIou else 'GEO'} {trainTitle} ===")
    print(f"Historical launches: {len(result_df)}")
    print(f"   Matched         : {matchedCount}")
    print(f"   Unmatched       : {unmatchedCount}")
    print(f"   Accuracy        : {matched.mean():.2%}")
    print("=" * 120)

    if isIou:
        for _, row in result_df.iterrows():
            match = (row["predicted_site"] == row["actual_site"] and row["predicted_rocket"] == row["actual_rocket"])
            if not match or match:
                print(
                    f"{row['file']} | "
                    f"{'OK' if match else 'NO'} |"
                    f"Actual: {row['actual_site']} × {row['actual_rocket']} | "
                    f"Predicted: {row['predicted_site']} × {row['predicted_rocket']} | "
                    f"Rank: {row['prediction_rank']} | "
                    f"Prob: {row['actual_probability']:.3f} | "
                    f"iou1: {row['actual_iou1']:6.2f}% |"
                    f"iou2: {row['actual_iou2']:6.2f}% |"
                    f"iou3: {row['actual_iou3']:6.2f}% |"
                    f"iou4: {row['actual_iou4']:6.2f}%"
                )
                for i, top in enumerate(row['top5'].split("|"), 1):
                    tops = top.split(":")
                    if i == 1:
                        print(f"\tTop 5:\t{tops[0].ljust(23 - len(tops[0]) + 3)} {tops[1]}")
                    else:
                        print(f"\t\t{tops[0].ljust(23 - len(tops[0]) + 3)} {tops[1]}")
                print()
    else:
        for _, row in result_df.iterrows():
            match = (row["predicted_site"] == row["actual_site"] and row["predicted_rocket"] == row["actual_rocket"])
            if not match:
                print(
                    f"{row['file']} | "
                    f"{'OK' if match else 'NO'} |"
                    f"Actual: {row['actual_site']} × {row['actual_rocket']} | "
                    f"Predicted: {row['predicted_site']} × {row['predicted_rocket']} | "
                    f"Rank: {row['combo_rank']} | "
                    f"Prob: {row['actual_probability']:.3f}"
                )
                for i, top in enumerate(row['top5'].split("|"), 1):
                    tops = top.split(":")
                    if i == 1:
                        print(f"\tTop 5:\t{tops[0].ljust(23 - len(tops[0]) + 3)} {tops[1]}")
                    else:
                        print(f"\t\t{tops[0].ljust(23 - len(tops[0]) + 3)} {tops[1]}")
                print()

    return result_df

# ============================================================
# Feature importance
# ============================================================
def show_feature_importance(model, feature_columns, train_df, test_df, debug=False):
    """
    Show which features Random Forest considered useful.
    """
    if debug:
        print()
        print(f"Training launches: {len(train_df)}")
        print(f"Testing launches:  {len(test_df)}")
        print(f"Model random state: {MODEL_RANDOM_STATE}")
        # print(f"Split random state: {SPLIT_RANDOM_STATE}")

        # print(train_df["rocket"].value_counts().sort_values(ascending=False))
        print(f"\nTraining samples by rocket:")
        print("   Rocket       Samples")
        s = train_df["rocket"].value_counts().sort_values(ascending=False)
        for i, (rocket, samples) in enumerate(s.items(), 1):
            rocket = rocket.ljust(12) if rocket.isascii() else rocket.ljust(12 - len(rocket))
            print(f"{i:02} {rocket} {samples}")

        # print(train_df.groupby(["site", "rocket"]).size().sort_values(ascending=False))
        print("\nTraining samples by site and rocket:")
        print("   Site       Rocket       Samples")
        s = train_df.groupby(["site", "rocket"]).size()
        siteSortDict = myConfig.readConfigSitesSortDict()
        s = s.loc[sorted(s.index, key=lambda x: (siteSortDict[x[0]], -s[x]))]
        last_site = ''

        for i, ((site, rocket), samples) in enumerate(s.items(), 1):
            if last_site == site:
                site = '          '
            else:
                last_site = site.ljust(10 - len(site))
            rocket = rocket.ljust(12) if rocket.isascii() else rocket.ljust(12 - len(rocket))
            samples = samples
            print(f"{i:02} {last_site} {rocket} {samples}")

    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps['preprocessor']
    feature_names = preprocessor.get_feature_names_out(feature_columns)
    importance = classifier.feature_importances_

    if debug:
        print()
        print(f"FEATURE NAME COMPARISON")
        print("=" * 50)
        if list(feature_columns) == list(feature_columns):
            print("Input feature columns/order       : IDENTICAL")
        else:
            print("Input feature columns/order       : DIFFERENT")
            for i, (a, b) in enumerate(zip(feature_columns, feature_columns)):
                if a != b:
                    print(f"First difference at {i}:")
                    print(f" model: {a}")
                    print(f"  prod: {b}")
                    break
        if list(feature_names) == list(feature_names):
            print("Preprocessor feature columns/order: IDENTICAL")
        else:
            print("Preprocessor feature columns/order: DIFFERENT")

            for i, (a, b) in enumerate(zip(feature_names, feature_names)):
                if a != b:
                    print(f"First difference at {i}:")
                    print(f" model: {a}")
                    print(f"  prod: {b}")
                    break

        print("\nModel feature check: ")
        print("=============================")
        print(" Input feature columns:", len(feature_columns))
        print(" Preprocessor features:", len(feature_names))
        print("GEO feature importances:", len(importance))
        if len(feature_names) != len(importance):
            print("   *** ERROR: feature name / importance length mismatch! ***")
        else:
            print("   *** OK: feature name and importances match.")

        import pandas as pd
        result = pd.DataFrame({"feature": feature_names, "importance": importance})
        result = result.sort_values("importance", ascending=False)
        print()
        print("=" * 60)
        print("TOP 30 FEATURES")
        print("=" * 60)
        print(f"Rank {'Features'.ljust(40)} Importance")
        heads = result.head(30)
        for i, row in enumerate(heads.itertuples()):
            feature1 = row.feature.rsplit("_", 1)[1]
            feature = row.feature.ljust(40) if feature1.isascii() else row.feature.ljust(40 - len(feature1))
            print(f"{i:02}   {feature} {row.importance:.4f}")

    feature_importance = pd.DataFrame({"feature": feature_names, "importance": classifier.feature_importances_})
    site_importance = feature_importance[feature_importance["feature"].str.startswith("cat__site_")]["importance"].sum()
    rocket_importance = feature_importance[feature_importance["feature"].str.startswith("cat__rocket_")]["importance"].sum()
    geometry_importance = feature_importance[feature_importance["feature"].str.startswith("num__")]["importance"].sum()
    print(f"\nGeometry Importance: {geometry_importance:.4f}")
    print(f"Site     Importance: {site_importance:.4f}")
    print(f"Rocket   Importance: {rocket_importance:.4f}")

# =====================================================================================
# Get rocket from filename, two types as below
#   2026年01月31日12时01分酒泉长征二号丙.kml laucnh from land
#   2026年03月27日12时11分酒泉长征二号丙远征一号商.kml laucnh with upper stage from land
#   2025年11月09日05时01分黄海海阳东方航天港号长征十一号海.kml launch from sea
# =====================================================================================
def get_rocket_from_filename(kml_path, raiseError=True):
    filename = Path(kml_path).stem
    # Check longer names first, e.g. 长征五号乙 before 长征五号
    rockets = myConfig.readConfigRockets(True)
    rockets = sorted(rockets, key=len, reverse=True)
    for rocket in rockets:
        if rocket in filename:
            return rocket.strip()
    
    if raiseError:
        raise ValueError(f"Cannot determine rocket from filename: {filename}")
    else:
        return UNKNOWN
    
# ============================================================
# Check new rocket
# ============================================================
def check_new_rocket(new_features, reference_features, feature_columns, threshold=3.0, k=5):
    """
    Check whether a new launch is sufficiently different
    from historical launches used by the production model.
    Site and site-interaction features are excluded.
    """
    # New launch -> one-row DataFrame
    import pandas as pd
    import numpy as np
    X_new = pd.DataFrame([new_features])

    # Keep only feature columns that are numeric.
    numeric_columns = [col for col in feature_columns if col in reference_features.columns and pd.api.types.is_numeric_dtype(reference_features[col])]
    X_reference = reference_features[numeric_columns].copy()
    X_new = X_new.reindex(columns=numeric_columns)

    # Remove columns that contain no usable historical values
    valid_columns = X_reference.columns[X_reference.notna().any(axis=0)]
    X_reference = X_reference[valid_columns]
    X_new = X_new[valid_columns]

    # Fill missing values using historical medians
    from sklearn.impute import SimpleImputer
    imputer = SimpleImputer(strategy="median")
    X_reference = imputer.fit_transform(X_reference)
    X_new = imputer.transform(X_new)

    # Scale using the historical reference data
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_reference_scaled = scaler.fit_transform(X_reference)
    X_new_scaled = scaler.transform(X_new)

    # Distance from new launch to every historical launch
    from sklearn.metrics import pairwise_distances
    distances = pairwise_distances(X_new_scaled, X_reference_scaled, metric="euclidean")[0]

    # Find nearest historical launches
    k = min(k, len(distances))
    nearest_distances = np.sort(distances)[:k]
    mean_distance = nearest_distances.mean()

    # New rocket decision
    new_rocket = mean_distance > threshold
    return new_rocket, mean_distance, nearest_distances

###############################################################################
def get_dz1_angle(launch_point, coordsList):
    """
    Calculate candidate DZ1 half-width angles.
    The angle is measured at the midpoint of a candidate side,
    between:
        1. midpoint -> launch point
        2. midpoint -> one endpoint of the side
    Candidates:
        - Always include the shortest candidate side.
        - Also include len1 (the northern side) when it is
          different from the shortest side.
    Returns:
        [
            {
                "length": ...,
                "side": (p1, p2),
                "midpoint": (...),
                "angle": ...
            },
            ...
        ]
    """
    import numpy as np
    results = []
    angles = []

    from shapely import Point
    if not isinstance(launch_point, Point):
        launch_point = Point(launch_point)

    # Spherical triangle:
    # A = launch point, B = midpoint, C = p2
    # a = BC, b = AC, c = AB
    from myModules import myShape
    for _, _, p1, p2 in myShape.get_shorter_sides(coordsList):
        # Midpoint of candidate side
        midpoint = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        a = myShape.angular_distance(midpoint[0], midpoint[1], p2[0], p2[1])
        b = myShape.angular_distance(launch_point.x, launch_point.y, p2[0], p2[1])
        c = myShape.angular_distance(launch_point.x, launch_point.y, midpoint[0], midpoint[1])
        numerator = cos(b) - cos(a) * cos(c)
        denominator = sin(a) * sin(c)

        if abs(denominator) < 1e-12:
            continue

        value = numerator / denominator

        # Protect acos from tiny floating-point errors.
        value = np.clip(value, -1.0, 1.0)
        angle_B_rad = min(acos(value), pi - acos(value))
        angles.append(angle_B_rad)
        results.append({"side": (p1, p2), "midpoint": midpoint, "angle": degrees(angle_B_rad),})

    angle = max(angles)
    results.append({"side": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), "midpoint": (0.0, 0.0), "angle": degrees(angle),})
    return angle

# ============================================================
# GEO Feature extraction
# ============================================================
def extract_geo_features(site, launch_point, mergedGdf, new_kml_path, rocket=None, debug=False):
    """
    Convert one launch KML into one feature dictionary.
    One KML = one ML sample.
    """
    from shapely import Point
    from myModules import myShape

    features = {}

    # angle: launch -> midpoint of DZ1 sides
    if "/circle" in mergedGdf.iloc[0].Name and mergedGdf.iloc[0].geometry.intersects(mergedGdf.iloc[1].geometry): 
        dz1 = mergedGdf.iloc[1]
    else:
        dz1 = mergedGdf.iloc[0]

    coordsList = list(dz1.geometry.exterior.coords)
    coordsList = coordsList[:-1] if coordsList[0] == coordsList[-1] else coordsList
    angle = get_dz1_angle(launch_point, coordsList)
    features["angle_diff"] = (90 - degrees(angle))

    if not isinstance(launch_point, Point):
        launch_point = Point(launch_point)

    j = 0
    for i, (dz, name) in enumerate(zip(mergedGdf.geometry, mergedGdf.Name)):
        if "/circle" in name and i < len(mergedGdf) - 1 and dz.intersects(mergedGdf.iloc[i + 1].geometry): 
            continue
        centroid = dz.centroid
        distance = myShape.geodesic_distance(launch_point, centroid)
        features[f"launch_dz{j + 1}_km"] = distance
        j += 1

    # File, Site, Rocket
    features["file"] = new_kml_path.name
    features["site"] = site
    if rocket:
        features["rocket"] = rocket

    if debug:
        print(f"{degrees(angle)=}")
        print(f"")

    return features

# ============================================================
# IoU Feature extraction
# ============================================================
def extract_iou_features(site, merged_gdf1, kml_file1, merged_gdf2, kml_file2, rocket1, rocket2, debug=False):
    """
    Convert one pair launch KMLs into one feature dictionary.
    One pair KMLs = one ML sample.
    """
    from myModules import myShape
    features = {}
    k = 1

    # TODO: if rocket is CZ-2F change first LineString to Polygon and calculate IoU
    for i, (dz1, name1) in enumerate(zip(merged_gdf1.geometry, merged_gdf1.Name)):
        if "/circle" in name1 and i < len(merged_gdf1) - 1 and dz1.intersects(merged_gdf1.iloc[i + 1].geometry):
            continue

        iouDz = []

        for j, (dz2, name2) in enumerate(zip(merged_gdf2.geometry, merged_gdf2.Name)):
            if "/circle" in name2 and j < len(merged_gdf2) - 1 and dz2.intersects(merged_gdf2.iloc[j + 1].geometry):
                continue

            intersection = dz1.intersection(dz2)
            if intersection:
                union = dz1.union(dz2)
                iou = intersection.area / union.area
                iouDz.append(iou)

        if iouDz:
            features[f"iou{k}"] = max(iouDz)
            k += 1

    # File, Site, Rocket
    features["file1"] = kml_file1
    features["file2"] = kml_file2
    features["site"] = site
    features["rocket1"] = rocket1
    features["rocket2"] = rocket2
    return features

###############################################################################
def get_distance_dzs(launch_point, dzGdf):
    dz_centroids = []
    distanceDict = {}

    from shapely import Point
    if not isinstance(launch_point, Point):
        launch_point = Point(launch_point)

    from myModules import myShape
    for i, dz in enumerate(dzGdf.geometry):
        centroid = dz.centroid
        dz_centroids.append(centroid)
        distance = myShape.geodesic_distance(launch_point, centroid)
        distanceDict[f"launch_dz{i + 1}_km"] = distance

    return distanceDict, dz_centroids

# ============================================================
# Predict a new launch with geometry features (site+rocket)
# ============================================================
def predict_geo_feature_classes_new(new_kml_path, model=MODEL_RADNOM_FOREST, debug=False):
    from myModules import myShape
    import pandas as pd
    import joblib

    if model == MODEL_HIST_GRADIENT_BOOSTING:
        model_name = "HGB"
        title = "HIST GRADIENT BOOSTING PREDICTION with GEO features and target CLASSES"
        prodModelFile = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_HIST_GRADIENT_BOOSTING)
    elif model == MODEL_GRADIENT_BOOSTING:
        model_name = "GB"
        title = "GRADIENT BOOSTING PREDICTION with GEO features and target CLASSES"
        prodModelFile = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_GRADIENT_BOOSTING)
    elif model == MODEL_EXTRA_TREES:
        model_name = "ET"
        title = f"EXTRA TREES PREDICTION with GEO features and target CLASSES"
        prodModelFile = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_EXTRA_TREES)
    else:
        model_name = "RF"
        title = f"RANDOM FOREST PREDICTION with GEO features and target CLASSES"
        prodModelFile = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_RADNOM_FOREST)


    print(f"\nLoad Production Model from file: {prodModelFile} ...")
    data = joblib.load(prodModelFile)

    geo_model = data["model"]
    filename_rocket = get_rocket_from_filename(new_kml_path, False)
    feature_columns = data["feature_columns"]

    # Extract normal KML features
    new_kml_path = Path(new_kml_path)
    gdf, mergedGdf, _, _ = myShape.parse_notam_kml_file(new_kml_path)
    if mergedGdf.empty:
        return

    fir_msa = myShape.get_fir_msa_From_kml(gdf)
    sites = myConfig.get_sites_from_fir_msa(fir_msa)
    all_results = []

    # Test every candidate site
    for site in sites:
        # Extract normal KML features
        launch_point = myConfig.getLaunchPointCoordinate(site)
        new_candidate_features_orig = extract_geo_features(site, launch_point, mergedGdf, new_kml_path)

        if new_candidate_features_orig:
            # Historical rocket candidates
            new_candidate_features = new_candidate_features_orig.copy()

            # Ensure exactly the same feature order
            X_new = pd.DataFrame([new_candidate_features])
            X_new = X_new.reindex(columns=feature_columns)

            # Predict new launch
            probabilities = geo_model.predict_proba(X_new)[0]

            if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
                classifier = geo_model[-1]
                X_tree = geo_model[:-1].transform(X_new)
                n_trees = len(classifier.estimators_)
                tree_votes = {}

                for tree in classifier.estimators_:
                    class_index = int(tree.predict(X_tree)[0])
                    class_name = classifier.classes_[class_index]
                    tree_votes[class_name] = tree_votes.get(class_name, 0) + 1

            for class_name, probability in zip(geo_model.classes_, probabilities):
                class_site, rocket = class_name.split("_")

                if class_site != site:
                    continue

                if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
                    all_results.append({
                        "site": site,
                        "rocket": rocket,
                        "probability": probability, 
                        "n_trees": n_trees,
                        "votes": tree_votes.get(class_name, 0),
                    })
                else:
                    all_results.append({
                        "site": site,
                        "rocket": rocket,
                        "probability": probability, 
                    })

    # Output
    result_df = pd.DataFrame(all_results)
    best_rocket_results = (result_df.sort_values(["probability"], ascending=False).reset_index(drop=True))

    filename_site = myShape.get_site_from_filename(new_kml_path, withDetai=True, raiseError=False)
    filename_upper_stage = myShape.get_upper_stage_from_filename(new_kml_path, False)

    print("=" * 90)
    print(title)
    print("=" * 90)
    print(f"New Launch File      : {new_kml_path.name}")
    print(f"Filename Rocket      : {filename_rocket}")
    print(f"Filename Site        : {filename_site}")
    print(f"Filename Upper Stage : {filename_upper_stage}") if filename_upper_stage else None
    print(f"1st FIR/MSA Code     : {fir_msa}")
    print(f"Candidate Sites      : {', '.join(sites)}")
    print("-" * 90)

    if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
        print(f"{model_name}-Rank  Rocket       Probability Votes     Site")
        for i, row in enumerate(best_rocket_results.head(10).itertuples(index=False), 1):
            if row.votes > 0:
                rocketName = (row.rocket.ljust(12) if row.rocket.isascii() else row.rocket.ljust(12 - len(row.rocket)))
                print(f"{i}\t {rocketName} {row.probability:.4f}\t  {row.votes:3d}/{row.n_trees}   {row.site}")
    else:
        print(f"{model_name}-Rank  Rocket       Probability  Site")
        for i, row in enumerate(best_rocket_results.head(10).itertuples(index=False), 1):
            if row.probability >= 0.0001:
                rocketName = (row.rocket.ljust(12) if row.rocket.isascii() else row.rocket.ljust(12 - len(row.rocket)))
                print(f"{i}\t  {rocketName} {row.probability:.4f}       {row.site}")

    # Best prediction
    predicSite = best_rocket_results.iloc[0]["site"]
    predicRocket = best_rocket_results.iloc[0]["rocket"]
    print("-" * 90)
    print(f"Prediction Site      : {predicSite}")
    print(f"Match                : {UNKNOWN if filename_site == UNKNOWN else 'YES' if filename_site == predicSite else 'NO'}")
    print(f"Prediction Rocket    : {predicRocket}")
    print(f"Match                : {UNKNOWN if filename_rocket == UNKNOWN else 'YES' if filename_rocket == predicRocket else 'NO'}")
    return best_rocket_results

# ============================================================
# Predict a new launch with geometry features
# ============================================================
def predict_geo_feature_binary_new(new_kml_path, model=MODEL_RADNOM_FOREST, debug=False):
    """
    Predict rocket for a new KML using Method #3.
    Method #3:
        X = site + rocket + geometry features
        y = target (0/1)
    Each historical rocket is tested as a candidate.
    The probability of target=1 is used as the candidate score.
    """
    from myModules import myShape
    import pandas as pd
    import numpy as np
    import joblib

    if model == MODEL_HIST_GRADIENT_BOOSTING:
        model_name = "HGB"
        title = "HIST GRADIENT BOOSTING PREDICTION with GEO features and target BINARY"
        prodModelFile = get_model_filename(GEO_FEATIRE_PKL, MODEL_HIST_GRADIENT_BOOSTING)
    elif model == MODEL_GRADIENT_BOOSTING:
        model_name = "GB"
        title = "GRADIENT BOOSTING PREDICTION with GEO features and target BINARY"
        prodModelFile = get_model_filename(GEO_FEATIRE_PKL, MODEL_GRADIENT_BOOSTING)
    elif model == MODEL_EXTRA_TREES:
        model_name = "ET"
        title = "EXTRA TREES PREDICTION with GEO features and target BINARY"
        prodModelFile = get_model_filename(GEO_FEATIRE_PKL, MODEL_EXTRA_TREES)
    else:
        model_name = "RF"
        title = "RANDOM FOREST PREDICTION with GEO features and target BINARY"
        prodModelFile = get_model_filename(GEO_FEATIRE_PKL, MODEL_RADNOM_FOREST)

    print(f"\nLoad Production Model from file: {prodModelFile} ...")
    data = joblib.load(prodModelFile)

    geo_model = data["model"]
    filename_rocket = get_rocket_from_filename(new_kml_path, False)
    feature_columns = data["feature_columns"]

    new_kml_path = Path(new_kml_path)
    gdf, mergedGdf, _, _ = myShape.parse_notam_kml_file(new_kml_path)

    if mergedGdf.empty:
        return

    fir_msa = myShape.get_fir_msa_From_kml(gdf)
    sites = myConfig.get_sites_from_fir_msa(fir_msa)
    all_results = []
    siteRocketsDict = myConfig.readConfigSiteRocketDict()

    # Test every candidate site
    for site in sites:
        # Extract normal KML features
        launch_point = myConfig.getLaunchPointCoordinate(site)
        new_candidate_features_orig = extract_geo_features(site, launch_point, mergedGdf, new_kml_path)

        if not new_candidate_features_orig:
            continue

        # Historical rocket candidates
        rocket_candidates = siteRocketsDict.get(site, ())

        # Test every historical rocket
        for history_rocket in rocket_candidates:
            new_candidate_features = new_candidate_features_orig.copy()
            new_candidate_features["rocket"] = history_rocket
            angle = 90 - new_candidate_features["angle_diff"]
            distance = new_candidate_features["launch_dz1_km"]

            # Ensure exactly the same feature order
            X_new = pd.DataFrame([new_candidate_features])
            X_new = X_new.reindex(columns=feature_columns)

            # check invalid production candidate
            siteDebug = X_new["site"].iloc[0]
            rocketDebug = X_new["rocket"].iloc[0]
            siteRocketsDict = myConfig.readConfigSiteRocketDict()
            if rocketDebug not in siteRocketsDict.get(siteDebug, ()):
                print(f"!!! INVALID PREDICTION CANDIDATE: {siteDebug} x {rocketDebug}")

            # Predict new launch
            probabilities = geo_model.predict_proba(X_new)[0]

            classifier = geo_model.named_steps["classifier"]
            classes = classifier.classes_
            target_index = np.where(classes == 1)[0][0]
            target_probability = probabilities[target_index]

            if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
                n_trees = len(classifier.estimators_)
                target_votes = target_probability * n_trees

                all_results.append({
                    "rocket": history_rocket, 
                    "site": site.ljust(9 - len(site)), 
                    "angle": angle, 
                    "probability": target_probability, 
                    "votes": target_votes,
                    "launch_dz1_km": distance,
                })
            else:
                all_results.append({
                    "rocket": history_rocket, 
                    "site": site.ljust(9 - len(site)), 
                    "angle": angle, 
                    "probability": target_probability, 
                    "launch_dz1_km": distance,
                })

    # Rank candidate rockets
    result_df = pd.DataFrame(all_results)
    result_df = result_df.sort_values(["angle", "probability"], ascending=False).reset_index(drop=True)
    result_df["angle_rank"] = result_df.index + 1
    best_rocket_results = (result_df.sort_values(["probability", "angle"], ascending=False).reset_index(drop=True))

    # Output
    filename_site = myShape.get_site_from_filename(new_kml_path, withDetai=True, raiseError=False)
    filename_upper_stage = myShape.get_upper_stage_from_filename(new_kml_path, False)

    print("=" * 90)
    print(title)
    print("=" * 90)
    print(f"New Launch File      : {new_kml_path.name}")
    print(f"Filename Rocket      : {filename_rocket}")
    print(f"Filename Site        : {filename_site}")
    print(f"Filename Upper Stage : {filename_upper_stage}") if filename_upper_stage else None
    print(f"1st FIR/MSA Code     : {fir_msa}")
    print(f"Candidate Sites      : {', '.join(sites)}")
    print("-" * 90)

    if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
        print(f"{model_name}-Rank  Rocket       Probability Votes  Site      Angle   Angle-Rank Distance")
        for i, row in enumerate(best_rocket_results.head(10).itertuples(index=False), 1):
            if row.votes > 0:
                rocketName = (row.rocket.ljust(12) if row.rocket.isascii() else row.rocket.ljust(12 - len(row.rocket)))
                print(f"{i}\t {rocketName} {row.probability:.4f}    {row.votes:3.0f}/{n_trees}  {row.site} {row.angle:5.2f}° {row.angle_rank:2d}\t {row.launch_dz1_km:4.0f}km")
    else:
        print(f"{model_name}-Rank  Rocket       Probability  Site      Angle   Angle-Rank Distance")
        for i, row in enumerate(best_rocket_results.head(10).itertuples(index=False), 1):
            if row.probability >= 0.0001:
                rocketName = (row.rocket.ljust(12) if row.rocket.isascii() else row.rocket.ljust(12 - len(row.rocket)))
                print(f"{i}\t  {rocketName} {row.probability:.4f}       {row.site} {row.angle:5.2f}° {row.angle_rank:2d}\t {row.launch_dz1_km:4.0f}km")

    # Best prediction
    predicSite = best_rocket_results.iloc[0]["site"].strip()
    predicRocket = best_rocket_results.iloc[0]["rocket"]
    print("-" * 90)
    print(f"Prediction Site      : {predicSite}")
    print(f"Match                : {UNKNOWN if filename_site == UNKNOWN else 'YES' if filename_site == predicSite else 'NO'}")
    print(f"Prediction Rocket    : {predicRocket}")
    print(f"Match                : {UNKNOWN if filename_rocket == UNKNOWN else 'YES' if filename_rocket == predicRocket else 'NO'}")
    return best_rocket_results

# ============================================================
# Predict a new launch with Intersection Over Union features
# ============================================================
def predict_iou_feature_binary_new(new_kml_path, model=MODEL_RADNOM_FOREST, debug=False):
    """
    Predict rocket for a new KML using IoU features.
        X = site + rocket + IoU features
        y = target (0/1)
    Each historical rocket is tested as a candidate.
    The probability of target=1 is used as the candidate score.
    """
    from myModules import myShape
    import pandas as pd
    import joblib

    if model == MODEL_HIST_GRADIENT_BOOSTING:
        model_name = "HGB"
        title = f"HIST GRADIENT BOOSTING PREDICTION with IoU features with target BINARY"
        prodModelFile = get_model_filename(IOU_FEATIRE_PKL, MODEL_HIST_GRADIENT_BOOSTING)
    elif model == MODEL_GRADIENT_BOOSTING:
        model_name = "GB"
        title = f"GRADIENT BOOSTING PREDICTION with IoU features with target BINARY"
        prodModelFile = get_model_filename(IOU_FEATIRE_PKL, MODEL_GRADIENT_BOOSTING)
    elif model == MODEL_EXTRA_TREES:
        model_name = "ET"
        title = f"EXTRA TREES PREDICTION with IoU features with target BINARY"
        prodModelFile = get_model_filename(IOU_FEATIRE_PKL, MODEL_EXTRA_TREES)
    else:
        model_name = "RF"
        title = f"RANDOM FOREST PREDICTION with IoU features with target BINARY"
        prodModelFile = get_model_filename(IOU_FEATIRE_PKL, MODEL_RADNOM_FOREST)

    print(f"\nLoad Production Model from file: {prodModelFile} ...")
    data = joblib.load(prodModelFile)

    iou_model = data["model"]
    filename_rocket = get_rocket_from_filename(new_kml_path, False)
    feature_columns = data["feature_columns"]

    new_kml_path = Path(new_kml_path)
    gdf, mergedDGdf, _, _ = myShape.parse_notam_kml_file(new_kml_path)

    fir_msa = myShape.get_fir_msa_From_kml(gdf)
    sites = myConfig.get_sites_from_fir_msa(fir_msa)
    siteFolders = myConfig.readConfigSitesFolders()

    X_newList = myExcept.run_function(f"Prepare Feature IoU Model {model}", prepare_iou_feature_new, sites, mergedDGdf, new_kml_path.name, feature_columns, siteFolders)
    all_results = myExcept.run_function(f"Predict Feature IoU Model {model}", predict_iou_feature, iou_model, X_newList, model)

    # Rank candidate rockets
    result_df = pd.DataFrame(all_results)
    result_df = result_df.sort_values(["iou", "probability"], ascending=False).reset_index(drop=True)
    result_df["iou_rank"] = result_df.index + 1
    best_rocket_results = (result_df.sort_values(["probability", "iou"], ascending=False).drop_duplicates(["site", "rocket"]).reset_index(drop=True))

    # Output
    filename_site = myShape.get_site_from_filename(new_kml_path, withDetai=False, raiseError=False)
    filename_upper_stage = myShape.get_upper_stage_from_filename(new_kml_path, False)

    print("=" * 90)
    print(title)
    print("=" * 90)
    print(f"New Launch File      : {new_kml_path.name}")
    print(f"Filename Rocket      : {filename_rocket}")
    print(f"Filename Site        : {filename_site}")
    print(f"Filename Upper Stage : {filename_upper_stage}") if filename_upper_stage else None
    print(f"1st FIR/MSA Code     : {fir_msa}")
    print(f"Candidate Sites      : {', '.join(sites)}")
    print("-" * 90)

    if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
        print(f"{model_name}-Rank  Rocket       Probability Votes     Site      IoU      IoU-Rank")
        for i, row in enumerate(best_rocket_results.head(10).itertuples(index=False), 1):
            if row.votes > 0:
                rocketName = (row.rocket.ljust(12) if row.rocket.isascii() else row.rocket.ljust(12 - len(row.rocket)))
                print(f"{i}\t {rocketName} {row.probability:.4f}      {row.votes:3.0f}/{row.n_trees}   {row.site} {row.iou:6.2f}%    {row.iou_rank:2d}")
    else:
        print(f"{model_name}-Rank  Rocket       Probability Site      IoU      IoU-Rank")
        for i, row in enumerate(best_rocket_results.head(10).itertuples(index=False), 1):
            if row.probability >= 0.0001:
                rocketName = (row.rocket.ljust(12) if row.rocket.isascii() else row.rocket.ljust(12 - len(row.rocket)))
                print(f"{i}\t  {rocketName} {row.probability:.4f}      {row.site} {row.iou:6.2f}%    {row.iou_rank:2d}")

    # Best prediction
    predicSite = best_rocket_results.iloc[0]["site"].strip()
    predicRocket = best_rocket_results.iloc[0]["rocket"]
    print("-" * 90)
    print(f"Prediction Site      : {predicSite}")
    print(f"Match                : {UNKNOWN if filename_site == UNKNOWN else 'YES' if filename_site == predicSite else 'NO'}")
    print(f"Prediction Rocket    : {predicRocket}")
    print(f"Match                : {UNKNOWN if filename_site == UNKNOWN else 'YES' if filename_rocket == predicRocket else 'NO'}")
    return best_rocket_results

# ----------------------------------------------------
# Prepare new launch feature IoU
# ----------------------------------------------------
def prepare_iou_feature_new(sites, new_merged_gdf, new_kml_file, feature_columns, siteFolders):
    X_newList = []

    # Test every candidate site
    for site in sites:
        X_news = myExcept.run_function(f"Prepare {site}", prepare_iou_feature_new_site, site, new_merged_gdf, new_kml_file, feature_columns, siteFolders)
        X_newList.extend(X_news)
    return X_newList

# ----------------------------------------------------
# Prepare new launch feature IoU for site
# ----------------------------------------------------
def prepare_iou_feature_new_site(site, new_merged_gdf, new_kml_file, feature_columns, siteFolders):
    import pandas as pd

    X_newList = []

    # Historical rocket candidates
    old_kml_paths = Path(siteFolders.get(site, KMLS_DIR)).rglob(f"*.kml")

    # Test every historical kml files
    for old_kml_path in old_kml_paths:
        if "old" in old_kml_path.parts:
            continue

        if "old" in old_kml_path.name.lower():
            continue

        # Extract normal KML features
        old_rocket = get_rocket_from_filename(old_kml_path)
        from myModules import myShape

        _, old_merged_gdf, _, _ = myShape.parse_notam_kml_file(old_kml_path)
        if old_merged_gdf.empty:
            continue

        new_candidate_features_orig = extract_iou_features(site, old_merged_gdf, old_kml_path.name, new_merged_gdf, new_kml_file, old_rocket, old_rocket)

        if not new_candidate_features_orig:
            continue

        if not any(k in new_candidate_features_orig for k in ["iou1", "iou2", "iou3"]):
            continue

        new_candidate_features = new_candidate_features_orig.copy()
        iou1 = new_candidate_features["iou1"] if "iou1" in new_candidate_features else 0.0
        iou2 = new_candidate_features["iou2"] if "iou2" in new_candidate_features else 0.0
        iou3 = new_candidate_features["iou3"] if "iou3" in new_candidate_features else 0.0
        iou = max(iou1, iou2, iou3)

        if iou == 0.0:
            continue

        # Ensure exactly the same feature order
        X_new = pd.DataFrame([new_candidate_features])
        X_new = X_new.reindex(columns=feature_columns)
        X_newList.append((X_new, site, old_rocket, iou))
    return X_newList

# ----------------------------------------------------
# Predict feature IoU
# ----------------------------------------------------
def predict_iou_feature(iou_model, X_newList, model=MODEL_RADNOM_FOREST):
    import numpy as np
    all_results = []

    for (X_new, site, history_rocket, iou) in X_newList:
        # check invalid production candidate
        # siteDebug = X_new["site"].iloc[0]
        # rocketDebug = X_new["rocket1"].iloc[0]
        # siteRocketsDict = myConfig.readConfigSiteRocketDict()
        # if rocketDebug not in siteRocketsDict.get(siteDebug, ()):
        #     print(f"!!! INVALID PREDICTION CANDIDATE: {siteDebug} x {rocketDebug}")

        # Predict new launch
        probabilities = iou_model.predict_proba(X_new)[0]

        classifier = iou_model.named_steps["classifier"]
        classes = classifier.classes_
        target_index = np.where(classes == 1)[0][0]
        target_probability = probabilities[target_index]

        if model == MODEL_RADNOM_FOREST or model == MODEL_EXTRA_TREES:
            n_trees = len(classifier.estimators_)
            target_votes = target_probability * n_trees
            all_results.append({
                "rocket": history_rocket, 
                "site": site.ljust(9 - len(site)), 
                "iou": iou * 100, 
                "probability": target_probability, 
                "votes": target_votes,
                "n_trees": n_trees,
            })
        else:
            all_results.append({
                "rocket": history_rocket, 
                "site": site.ljust(9 - len(site)), 
                "iou": iou * 100, 
                "probability": target_probability, 
            })
    return all_results

# ============================================================
# Evaluate New Rocket Distance
# ============================================================
def detect_new_rocket_pattern(df, trainRate=(0.80, 0.85, 0.90, 0.95), debug=False):
    for rate in trainRate:
        train_df, test_df = chronological_split_per_site_rocket(df, rate)
        model, _ = build_model_rf(train_df)
        report_train_test_ranking(model, test_df, rate)

# ============================================================
# Analyse Site Sensitivity
# ============================================================
def analyze_site_sensitivity(model, new_df, feature_columns, all_rows=False, debug=False):
    """
        Analyze model sensitivity.
        withSite=True:
            Analyze sensitivity to launch site.
            The site is changed to every possible site while all
            other features remain unchanged.
        withSite=False:
            Analyze rocket prediction sensitivity.
            No site information is required. The model predicts the
            supplied launches and reports sensitivity/recall for each rocket.
        withSite=None:
            Automatically detect whether the model has site_values_.
        all_rows=False:
            Analyze only the first launch.
        all_rows=True:
            Analyze all launches.
        """
    import numpy as np
    # Automatically detect model type if not explicitly specified
    results = []
    classes = model.classes_

    # Select rows to analyze
    if all_rows:
        X_source = new_df.copy()
    else:
        X_source = new_df.iloc[[0]].copy()

    # Test every possible site
    candidate_sites = []
    for site in candidate_sites:
        X_test = X_source.copy()

        # Change only site
        X_test["site"] = site

        # Keep exactly the features used by the model
        X_test = X_test.reindex(columns=feature_columns, fill_value=0)

        # Predict
        probabilities = model.predict_proba(X_test[feature_columns])

        # First-row mode
        if not all_rows:
            probabilities = probabilities[0]
            order = probabilities.argsort()[::-1]
            top_index = order[0]
            top_class = classes[top_index]
            top_probability = probabilities[top_index]
            results.append({"site": site, "prediction": top_class, "probability": top_probability})

        # All-row mode
        else:
            import pandas as pd
            top_indices = np.argmax(probabilities, axis=1)
            top_classes = classes[top_indices]
            top_probabilities = probabilities[np.arange(len(probabilities)), top_indices]
            prediction_counts = pd.Series(top_classes).value_counts()
            top_class = prediction_counts.index[0]
            results.append({
                "site": site,
                "prediction": top_class,
                "probability": top_probabilities.mean(),
                "prediction_count": prediction_counts.iloc[0],
                "prediction_rate": (prediction_counts.iloc[0] / len(top_classes))
            })

    # Sort
    results.sort(key=lambda x: x["probability"], reverse=True)

    # Display
    if debug:
        print()
        print(f"Site Interaction Sensitivity")

        if all_rows:
            print(f"Analyzed launches: {len(X_source)}")

        print("-" * 70)

        for i, result in enumerate(results, 1):
            if all_rows:
                print(f"{i:02d} {result['site']} {result['prediction'].ljust(12)} {result['probability']:.3f} ({result['prediction_rate']:.1%})")
            else:
                print(f"{i:02d} {result['site']} {result['prediction'].ljust(12)} {result['probability']:.3f}")
    return results

# ============================================================
# Build Train Model
# ============================================================
def build_prod_model(iou_df, new_iou_rows, geo_df, new_geo_rows, geo_site_rocket_df, debug=False):
    if not iou_df.empty:
        modelFilename_rf = get_model_filename(IOU_FEATIRE_PKL, MODEL_RADNOM_FOREST)
        modelFilename_et = get_model_filename(IOU_FEATIRE_PKL, MODEL_EXTRA_TREES)
        modelFilename_gb = get_model_filename(IOU_FEATIRE_PKL, MODEL_GRADIENT_BOOSTING)
        modelFilename_hgb = get_model_filename(IOU_FEATIRE_PKL, MODEL_HIST_GRADIENT_BOOSTING)

        if new_iou_rows:
            prod_iou_df = iou_df.copy()
            prod_iou_df, _ = chronological_split(prod_iou_df, isIou=True)

            model_iou_rf, feature_columns_iou = build_model_rf(prod_iou_df, isIou=True)
            save_prod_model(modelFilename_rf, prod_iou_df, feature_columns_iou, model_iou_rf, isIou=True)

            model_iou_et, feature_columns_iou = build_model_et(prod_iou_df, isIou=True)
            save_prod_model(modelFilename_et, prod_iou_df, feature_columns_iou, model_iou_et, isIou=True)

            model_iou_gb, feature_columns_iou = build_model_gb(prod_iou_df, isIou=True)
            save_prod_model(modelFilename_gb, prod_iou_df, feature_columns_iou, model_iou_gb, isIou=True)

            model_iou_hgb, feature_columns_iou = build_model_hgb(prod_iou_df, isIou=True)
            save_prod_model(modelFilename_hgb, prod_iou_df, feature_columns_iou, model_iou_hgb, isIou=True)
        else:
            if not modelFilename_rf.is_file():
                prod_iou_df = iou_df.copy()
                prod_iou_df, _ = chronological_split(prod_iou_df, isIou=True)
                model_iou_rf, feature_columns_iou = build_model_rf(prod_iou_df, isIou=True)
                save_prod_model(modelFilename_rf, prod_iou_df, feature_columns_iou, model_iou_rf, isIou=True)
                
            if not modelFilename_et.is_file():
                prod_iou_df = iou_df.copy()
                prod_iou_df, _ = chronological_split(prod_iou_df, isIou=True)
                model_iou_et, feature_columns_iou = build_model_et(prod_iou_df, isIou=True)
                save_prod_model(modelFilename_et, prod_iou_df, feature_columns_iou, model_iou_et, isIou=True)
                
            if not modelFilename_gb.is_file():
                prod_iou_df = iou_df.copy()
                prod_iou_df, _ = chronological_split(prod_iou_df, isIou=True)
                model_iou_gb, feature_columns_iou = build_model_gb(prod_iou_df, isIou=True, subsample=1.0)
                save_prod_model(modelFilename_gb, prod_iou_df, feature_columns_iou, model_iou_gb, isIou=True)
                
            if not modelFilename_hgb.is_file():
                prod_iou_df = iou_df.copy()
                prod_iou_df, _ = chronological_split(prod_iou_df, isIou=True)
                model_iou_hgb, feature_columns_iou = build_model_hgb(prod_iou_df, isIou=True)
                save_prod_model(modelFilename_hgb, prod_iou_df, feature_columns_iou, model_iou_hgb, isIou=True)

    if not geo_df.empty:
        modelFilename_rf = get_model_filename(GEO_FEATIRE_PKL, MODEL_RADNOM_FOREST)
        modelFilename_et = get_model_filename(GEO_FEATIRE_PKL, MODEL_EXTRA_TREES)
        modelFilename_gb = get_model_filename(GEO_FEATIRE_PKL, MODEL_GRADIENT_BOOSTING)
        modelFilename_hgb = get_model_filename(GEO_FEATIRE_PKL, MODEL_HIST_GRADIENT_BOOSTING)

        if new_geo_rows:
            prod_geo_df = geo_df.copy()
            prod_geo_df, _ = chronological_split(prod_geo_df)

            model_geo_rf, feature_columns_geo = build_model_rf(prod_geo_df)
            save_prod_model(modelFilename_rf, prod_geo_df, feature_columns_geo, model_geo_rf)

            model_geo_et, feature_columns_geo = build_model_et(prod_geo_df)
            save_prod_model(modelFilename_et, prod_geo_df, feature_columns_geo, model_geo_et)

            model_geo_gb, feature_columns_geo = build_model_gb(prod_geo_df)
            save_prod_model(modelFilename_gb, prod_geo_df, feature_columns_geo, model_geo_gb)

            model_geo_hgb, feature_columns_geo = build_model_hgb(prod_geo_df)
            save_prod_model(modelFilename_hgb, prod_geo_df, feature_columns_geo, model_geo_hgb)
        else:
            if not modelFilename_rf.is_file():
                prod_geo_df = geo_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_rf, feature_columns_geo = build_model_rf(prod_geo_df)
                save_prod_model(modelFilename_rf, prod_geo_df, feature_columns_geo, model_geo_rf)

            if not modelFilename_et.is_file():
                prod_geo_df = geo_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_et, feature_columns_geo = build_model_et(prod_geo_df)
                save_prod_model(modelFilename_et, prod_geo_df, feature_columns_geo, model_geo_et)

            if not modelFilename_gb.is_file():
                prod_geo_df = geo_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_gb, feature_columns_geo = build_model_gb(prod_geo_df, subsample=1.0)
                save_prod_model(modelFilename_gb, prod_geo_df, feature_columns_geo, model_geo_gb)

            if not modelFilename_hgb.is_file():
                prod_geo_df = geo_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_hgb, feature_columns_geo = build_model_hgb(prod_geo_df)
                save_prod_model(modelFilename_hgb, prod_geo_df, feature_columns_geo, model_geo_hgb)

    if not geo_site_rocket_df.empty:
        modelFilename_rf = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_RADNOM_FOREST)
        modelFilename_et = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_EXTRA_TREES)
        modelFilename_gb = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_GRADIENT_BOOSTING)
        modelFilename_hgb = get_model_filename(GEO_SITE_ROCKET_FEATIRE_PKL, MODEL_HIST_GRADIENT_BOOSTING)

        if new_geo_rows:
            prod_geo_df = geo_site_rocket_df.copy()
            prod_geo_df, _ = chronological_split(prod_geo_df)

            model_geo_rf, feature_columns_geo = build_model_rf(prod_geo_df, isSiteRocket=True)
            save_prod_model(modelFilename_rf, prod_geo_df, feature_columns_geo, model_geo_rf)

            model_geo_et, feature_columns_geo = build_model_et(prod_geo_df, isSiteRocket=True)
            save_prod_model(modelFilename_et, prod_geo_df, feature_columns_geo, model_geo_et)

            model_geo_gb, feature_columns_geo = build_model_gb(prod_geo_df, isSiteRocket=True, subsample=1.0)
            save_prod_model(modelFilename_gb, prod_geo_df, feature_columns_geo, model_geo_gb)

            model_geo_hgb, feature_columns_geo = build_model_hgb(prod_geo_df, isSiteRocket=True)
            save_prod_model(modelFilename_hgb, prod_geo_df, feature_columns_geo, model_geo_hgb)
        else:
            if not modelFilename_rf.is_file():
                prod_geo_df = geo_site_rocket_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_rf, feature_columns_geo = build_model_rf(prod_geo_df, isSiteRocket=True)
                save_prod_model(modelFilename_rf, prod_geo_df, feature_columns_geo, model_geo_rf)

            if not modelFilename_et.is_file():
                prod_geo_df = geo_site_rocket_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_et, feature_columns_geo = build_model_et(prod_geo_df, isSiteRocket=True)
                save_prod_model(modelFilename_et, prod_geo_df, feature_columns_geo, model_geo_et)

            if not modelFilename_gb.is_file():
                prod_geo_df = geo_site_rocket_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_gb, feature_columns_geo = build_model_gb(prod_geo_df, isSiteRocket=True, subsample=1.0)
                save_prod_model(modelFilename_gb, prod_geo_df, feature_columns_geo, model_geo_gb)

            if not modelFilename_hgb.is_file():
                prod_geo_df = geo_site_rocket_df.copy()
                prod_geo_df, _ = chronological_split(prod_geo_df)
                model_geo_hgb, feature_columns_geo = build_model_hgb(prod_geo_df, isSiteRocket=True)
                save_prod_model(modelFilename_hgb, prod_geo_df, feature_columns_geo, model_geo_hgb)

# ============================================================
# train test model
# ============================================================
def train_test_model(geo_df, iou_df, trainRate=0.80, debug=False, inspect=False):
    # train/test GEO features
    geo_train_df, geo_test_df = chronological_split_per_site_rocket(geo_df, isIou=False, trainRate=trainRate)

    # train/test RF Model
    geo_model_rf, geo_feature_columns_rf = build_model_rf(geo_train_df, isIou=False) # Train model
    result_df = report_train_test_ranking(geo_model_rf, geo_test_df, isIou=False, isHgb=False, trainRate=trainRate)

    # train/test HGB Model
    geo_model_hgb, geo_feature_columns_hgb = build_model_hgb(geo_train_df, isIou=False) # Train model
    result_df = report_train_test_ranking(geo_model_hgb, geo_test_df, isIou=False, isHgb=True, trainRate=trainRate)

    # train/test IoU features
    iou_train_df, iou_test_df = chronological_split_per_site_rocket(iou_df, isIou=True, trainRate=trainRate)

    # train/test RF Model
    iou_model_rf, iou_feature_columns_rf = build_model_rf(iou_train_df, isIou=True) # Train model
    result_df = report_train_test_ranking(iou_model_rf, iou_test_df, isIou=True, isHgb=False, trainRate=trainRate)

    # train/test HGB Model
    iou_model_hgb, iou_feature_columns_hgb = build_model_hgb(iou_train_df, isIou=True) # Train model
    result_df = report_train_test_ranking(iou_model_hgb, iou_test_df, isIou=True, isHgb=True, trainRate=trainRate)

    # show_angle_split_node_thresholds(geo_model_rf)

    # # Inspect Random Forest Model
    # if inspect:
    #     inspect_geo_angle_diff(geo_model_rf, geo_train_df, geo_feature_columns_rf)
    #     return

    # # Check test_df
    # if debug:
    #     check_method3_candidates(geo_test_df)

    #     show_unseen_results(result_df, geo_train_df)

    #     # 4. Evaluate Model
    #     evaluate_model(geo_model_rf, geo_train_df, geo_test_df, geo_feature_columns_rf) # Test model

    #     # 5. Show feature importance
    #     show_feature_importance(geo_model_rf, geo_feature_columns_rf, geo_train_df, geo_test_df, debug=False) # Show what the model learned

    #     if geo_model_rf.named_steps["classifier"].oob_score:
    #         actual, _ = show_oob_ranking_results(geo_model_rf, geo_train_df)
    #         show_oob_by_site(actual)
    #         show_oob_by_rocket(actual)
    #         show_oob_by_site_rocket(actual)

        # 6. Site sensitivity analysis
        # analyze_site_sensitivity(model, test_df, feature_columns, all_rows=True)

# ============================================================
# Inspect Random Forest Angle Diff
# ============================================================
def show_angle_split_node_thresholds(model, debug=False):
    import numpy as np

    if debug:
        feature_names = (model.named_steps["preprocessor"].get_feature_names_out())
        clf = model.named_steps["classifier"]
        angle_index = list(feature_names).index("num__angle_diff")
        angle_thresholds = []
        for tree_model in clf.estimators_:
            tree = tree_model.tree_
            mask = tree.feature == angle_index
            angle_thresholds.extend(tree.threshold[mask])

        angle_thresholds = np.array(angle_thresholds)

        from matplotlib import pyplot as plt
        from matplotlib.ticker import FuncFormatter
        plt.figure(figsize=(10, 5))
        plt.hist(angle_thresholds, bins=np.where(0, 95, 5), edgecolor="black")
        plt.xlabel("angle_diff threshold (degrees)")
        plt.ylabel("Number of split modes")
        plt.title("Random Forest Angle Split Thresholds")
        plt.xticks(np.arange(0, 91, 5))
        plt.grid(axis="y", alpha=0.3)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{int(x):,}"))
        plt.show()

    if debug:
        limit = 17.5
        count = np.sum(angle_thresholds <= limit)
        total = len(angle_thresholds)
        percentage = count / total * 100
        print("The Angle Split Nodes and Thresholds")
        print("=" * 40)
        print(f"Min Thresholds             : {angle_thresholds.min():5.2f}°")
        print(f"Max Thresholds             : {angle_thresholds.max():5.2f}°")
        print(f"Total Angle Split Nodes    : {total:,}")
        print(f"Angle Split Nodes <= {limit}°: {count:,}")
        print(f"Percentage                 : {percentage:.2f}%")

# ============================================================
# Inspect Random Forest Angle Diff
# ============================================================
def inspect_geo_angle_diff(model, train_df, feature_columns, debug=False):
    """
    Inspect how an already-fitted Random Forest uses angle_diff.
    This function does NOT fit, retrain, or modify the model.
    """
    import numpy as np
    model._angle_demo_row = train_df.iloc[[0]][feature_columns]
    clf = model.named_steps["classifier"]
    feature_names = (model.named_steps["preprocessor"].get_feature_names_out())

    # #1. Find angle_diff thresholds learned by the trees
    angle_indices = np.where(feature_names == "num__angle_diff")[0]

    angle_index = angle_indices[0]
    thresholds = []
    node_count = np.zeros(len(feature_names), dtype=int)

    for tree_no, tree_model in enumerate(clf.estimators_, start=1):
        tree = tree_model.tree_

        for node in range(tree.node_count):
            if tree.feature[node] == angle_index:
                thresholds.append({"tree": tree_no, "node": node, "threshold": tree.threshold[node]})

            if debug:
                for feature_index in tree.feature:
                    if feature_index >= 0:
                        node_count[feature_index] += 1

    if debug:
        import pandas as pd
        feature_stats = pd.DataFrame({"feature": feature_names, "node_count": node_count, "importance": clf.feature_importances_})
        feature_stats = feature_stats.sort_values("importance", ascending=False)

    # #1. Show angle_diff THRESHOLDS
    print()
    print("=" * 80)
    print("#1 LEARNED angle_diff THRESHOLDS")
    print("=" * 80)
    print(f"Trees in forest: {len(clf.estimators_)}")
    print(f"Trees using angle_diff: {len(set(x['tree'] for x in thresholds))}")
    print(f"Total angle_diff splits: {len(thresholds)}")

    if thresholds:
        threshold_values = [x["threshold"] for x in thresholds]
        print()
        print(f"Minimum threshold: {min(threshold_values):.3f}°")
        print(f"Maximum threshold: {max(threshold_values):.3f}°")
        print(f"Median threshold : {np.median(threshold_values):.3f}°")
        print()
        print("First learned thresholds:")

        for x in thresholds[:30]:
            print(f"Tree {x['tree']:3d}, node {x['node']:3d}: angle_diff <= {x['threshold']:5.2f}°")

        if debug:
            from matplotlib import pyplot as plt
            # Plot threshold distribution
            plt.figure(figsize=(10, 4.5))
            plt.hist(threshold_values, bins=20)

            plt.xlabel("Learned angle_diff threshold (degrees)")
            plt.ylabel("Number of splits")
            plt.title("Random Forest: learned angle_diff thresholds")
            plt.grid(True, alpha=0.25)
            plt.tight_layout()
            plt.xticks(np.arange(0, 91, 5))
            plt.show()

    # #2. Show one real tree
    print()
    print("=" * 80)
    print("#2 ONE REAL DECISION TREE")
    print("=" * 80)

    tree_no = 0
    tree_model = clf.estimators_[tree_no]

    if debug:
        print("Showing Tree 1 of the Random Forest.")
        plt.figure(figsize=(20, 10))

        import matplotlib.font_manager as fm
        fontPath = './fonts/simkai.ttf'
        fm.fontManager.addfont(fontPath)
        cn_font = fm.FontProperties(fname=fontPath)
        plt.rcParams['font.family'] = cn_font.get_name()
        plt.rcParams['axes.unicode_minus'] = False

        feature_names = (model.named_steps["preprocessor"].get_feature_names_out())

        from sklearn.tree import plot_tree
        plot_tree(tree_model, feature_names=feature_names, class_names=["0", "1"], filled=True, rounded=True, max_depth=4, fontsize=8)
        plt.title("One decision tree from the existing Random Forest")
        plt.tight_layout()
        plt.show()

    # #3. Show RF response as angle_diff changes
    print()
    print("=" * 80)
    print("#3 RF RESPONSE TO angle_diff")
    print("=" * 80)
    print("This section changes only angle_diff and keeps the other features fixed.")

    # Use the first row of the existing training data as a template.
    # If your pipeline/model does not retain the training DataFrame,
    # this section can instead accept one candidate row.
    if not hasattr(model, "_angle_demo_row"):
        print()
        print("To run #3, attach one existing feature row like this:")
        print()
        print("model._angle_demo_row = train_df.iloc[[0]][feature_columns]")
        print()
        print("Then run this function again.")
        return

    demo_row = model._angle_demo_row.copy()
    angle_values = np.linspace(0, 90, 181)

    demo_df = demo_row.loc[demo_row.index.repeat(len(angle_values))].reset_index(drop=True)
    demo_df["angle_diff"] = angle_values
    probabilities = model.predict_proba(demo_df)[:, 1]

    print(" Angle  Probability")
    for angle, prob in zip(angle_values, probabilities):
        print(f"{angle:5.2f}°  {prob:.4f}")

    if debug:
        plt.figure(figsize=(10, 5))
        plt.plot(angle_values, probabilities, linewidth=2)

        plt.xlabel("angle_diff (degrees)")
        plt.ylabel("RF P(target=1)")
        plt.title("Existing Random Forest response to angle_diff")
        plt.xlim(0, 90)
        plt.ylim(0, 0.06)
        plt.xticks(np.arange(0, 91, 10))
        plt.yticks(np.arange(0, 0.06, 0.005))

        plt.grid(True, alpha=0.25)
        plt.tight_layout()
        plt.show()

    # #4. Show FEATURE USAGE and IMPORTANCE
    if debug:
        print()
        print("=" * 80)
        print("#4 LEARNED FEATURE USAGE and IMPORTANCE")
        print("=" * 80)
        print(f"{'Feature'.ljust(40)} Node_count  Importance")
        for row in feature_stats.itertuples():
            feature = row.feature.ljust(40) if row.feature.isascii() else row.feature.ljust(40 - len(row.feature.split("_")[-1]) )
            print(f"{feature} {row.node_count:10,d}  {row.importance:.4f}")

# ============================================================
# Show Unseen Results
# ============================================================
def show_unseen_results(result_df, train_history):
    train_sites = set(train_history["site"])
    train_rockets = set(train_history["rocket"])
    train_site_rocket = set(zip(train_history["site"], train_history["rocket"]))

    result_df = result_df.copy()
    result_df["site_seen"] = result_df["actual_site"].isin(train_sites)
    result_df["rocket_seen"] = result_df["actual_rocket"].isin(train_rockets)
    result_df["site_rocket_seen"] = [(site, rocket) in train_site_rocket for site, rocket in zip(result_df["actual_site"], result_df["actual_rocket"])]

    print()
    print("=" * 60)
    print("RESULTS FOR SEEN / UNSEEN SITE + ROCKET")
    print("=" * 60)

    groups = {
        "Seen site + rocket": result_df["site_rocket_seen"],
        "New site + rocket combination": (result_df["site_seen"] & result_df["rocket_seen"] & ~result_df["site_rocket_seen"]),
        "New rocket": ~result_df["rocket_seen"]
    }

    for name, mask in groups.items():
        group = result_df[mask]

        if len(group) == 0:
            continue

        print(f"\n{name}: N={len(group)}")

        for k in [1, 2, 3, 5, 10]:
            count = (group["combo_rank"] <= k).sum()
            accuracy = count / len(group)
            print(f"Top-{k:02}: {count}/{len(group)} ({accuracy * 100:.2f}%)")

    print()
    print(result_df[["site_seen", "rocket_seen", "site_rocket_seen"]].value_counts())
    return result_df

# ============================================================
# Show OOB By Site x Rocket
# ============================================================
def show_oob_by_site_rocket(actual):
    print()
    print("=" * 60)
    print("OOB LAUNCH-LEVEL RESULTS BY SITE + ROCKET")
    print("=" * 60)
    rows = []

    for (site, rocket), group in actual.groupby(["site", "rocket"]):
        row = {"site": site, "rocket": rocket, "launches": len(group)}

        for k in [1, 2, 3, 5, 10]:
            count = (group["oob_rank"] <= k).sum()
            row[f"top{k}"] = count / len(group)

        rows.append(row)

    import pandas as pd
    result = pd.DataFrame(rows)
    result = result.sort_values(["top1", "launches"], ascending=[True, False])

    for _, row in result.iterrows():
        print(
            f"{row['site'].ljust(10 - len(row['site']))} "
            f"{row['rocket'].ljust(12) if row['rocket'].isascii() else row['rocket'].ljust(12 - len(row['rocket']))} "
            f"N={int(row['launches']):3d} "
            f"Top-1={row['top1'] * 100:6.2f}% "
            f"Top-2={row['top2'] * 100:6.2f}% "
            f"Top-3={row['top3'] * 100:6.2f}% "
            f"Top-5={row['top5'] * 100:6.2f}% "
            f"Top-10={row['top10'] * 100:6.2f}%"
        )
    return result

# ============================================================
# Show OOB By Site
# ============================================================
def show_oob_by_site(actual):
    print()
    print("=" * 60)
    print("OOB LAUNCH-LEVEL RESULTS BY SITE")
    print("=" * 60)
    rows = []

    for site, group in actual.groupby("site"):
        row = {"site": site, "launches": len(group),}

        for k in [1, 2, 3, 5, 10]:
            count = (group["oob_rank"] <= k).sum()
            accuracy = count / len(group)
            row[f"top{k}"] = accuracy

        rows.append(row)

    import pandas as pd
    result = pd.DataFrame(rows)

    for _, row in result.iterrows():
        print(
            f"{row['site'].ljust(10 - len(row['site']))} "
            f"N={int(row['launches']):3d}  "
            f"Top-1={row['top1'] * 100:6.2f}%  "
            f"Top-2={row['top2'] * 100:6.2f}%  "
            f"Top-3={row['top3'] * 100:6.2f}%  "
            f"Top-5={row['top5'] * 100:6.2f}%  "
            f"Top-10={row['top10'] * 100:6.2f}%"
        )
    return result

# ============================================================
# Show OOB By Rocket
# ============================================================
def show_oob_by_rocket(actual):
    print()
    print("=" * 60)
    print("OOB LAUNCH-LEVEL RESULTS BY ROCKET")
    print("=" * 60)
    rows = []

    for rocket, group in actual.groupby("rocket"):
        row = {"rocket": rocket, "launches": len(group),}

        for k in [1, 2, 3, 5, 10]:
            count = (group["oob_rank"] <= k).sum()
            accuracy = count / len(group)
            row[f"top{k}"] = accuracy

        rows.append(row)

    import pandas as pd
    result = pd.DataFrame(rows)

    for _, row in result.iterrows():
        print(
            f"{row['rocket'].ljust(12) if row['rocket'].isascii() else row['rocket'].ljust(12 - len(row['rocket']))} "
            f"N={int(row['launches']):3d}  "
            f"Top-1={row['top1'] * 100:6.2f}%  "
            f"Top-2={row['top2'] * 100:6.2f}%  "
            f"Top-3={row['top3'] * 100:6.2f}%  "
            f"Top-5={row['top5'] * 100:6.2f}%  "
            f"Top-10={row['top10'] * 100:6.2f}%"
        )
    return result

# ============================================================
# Show OOB Ranking Results
# ============================================================
def show_oob_ranking_results(model, train_df):
    clf = model.named_steps["classifier"]
    oob_proba = clf.oob_decision_function_
    result_df = train_df.copy()
    result_df["oob_prob"] = oob_proba[:, 1]

    # Rank candidates within each historical launch
    result_df["oob_rank"] = (result_df.groupby("file")["oob_prob"].rank(ascending=False, method="first"))

    # Only positive row is the actual site + rocket
    actual = result_df[result_df["target"] == 1].copy()

    # Rank statistics
    print("=" * 60)
    print("OOB LAUNCH-LEVEL RANKING")
    print("=" * 60)
    print(f"Historical launches: {len(actual)}")

    for k in [1, 2, 3, 5, 10]:
        count = (actual["oob_rank"] <= k).sum()
        accuracy = count / len(actual)
        print(f"Top-{k:02}: {count}/{len(actual)} ({accuracy * 100:.2f}%)")

    # Show failures
    wrong = actual[actual["oob_rank"] > 1].copy()
    print()
    print("-" * 100)
    print("OOB LAUNCH-LEVEL FAILURES")
    print("-" * 100)
    print(f"Top-1 wrong: {len(wrong)}/{len(actual)}")
    columns = ["file", "site", "rocket", "oob_rank", "oob_prob"]
    columns = [col for col in columns if col in wrong.columns]
    oobDf = wrong[columns].sort_values("oob_rank")
    print(f"{'File'.ljust(60)} {'Site'.ljust(10)} {'Rocket'.ljust(12)} OOB_Rank OOB_Probability")
    for row in oobDf.itertuples():
        dbcs_len = (len(row.file.encode("UTF-8")) - len(row.file)) // 2
        print(f"{row.file.ljust(60 - dbcs_len)} {row.site.ljust(10 - len(row.site))} {row.rocket.ljust(12 - len(row.rocket))}  {int(row.oob_rank):2d}       {row.oob_prob:.4f}")
    return actual, wrong

# len(text) = counts characters 1 for both DBCS and SBCS
# len(text.encode("UTF-8")) = counts bytes 1 for SBCS and 2 for DBCS
# len(text.encode("UTF-8")) - len(text) = counts 2 for DBCS only
# ============================================================
# check method3 candidates
# ============================================================
def check_method3_candidates(candidate_df):
    feature_columns = [
        "angle_diff",
        "launch_dz1_km",
        "launch_dz2_km",
        "launch_dz3_km",
        "launch_dz4_km",
        "site",
        "rocket"
    ]

    print("Rows:", len(candidate_df))
    print("Files:", candidate_df["file"].nunique())
    print("Site × Rocket:", candidate_df[["site", "rocket"]].drop_duplicates().shape[0])

    # Each launch should have one positive candidate
    positive_counts = candidate_df.groupby("file")["target"].sum()

    print("\nPositive candidates per launch:")
    print(positive_counts.value_counts().sort_index())

    # Show one launch
    file = candidate_df["file"].iloc[0]
    sample = candidate_df[candidate_df["file"] == file].copy()

    print("\nSample launch:", file)
    print(
        sample[
            [
                "site",
                "rocket",
                "target",
                "angle_diff",
                "launch_dz1_km",
                "launch_dz2_km",
                "launch_dz3_km",
                "launch_dz4_km",
            ]
        ].sort_values(["site", "rocket"]).to_string(index=False)
    )

# ============================================================
# get model filename
# ============================================================
def get_model_filename(model_file, model):
    modelFilename = model_file
    modelFilename = modelFilename.with_stem(f"{modelFilename.stem}-{model}")
    return modelFilename

# ============================================================
# Save model to pkl files
# ============================================================
def save_prod_model(modelFilename, df, feature_columns, model, isIou=False, debug=False):
    if isIou:
        class_counts = df["rocket1"].value_counts().to_dict()
    else:
        class_counts = df["rocket"].value_counts().to_dict()

    model_data = {
        "model": model,
        "reference_features": df,
        "feature_columns": feature_columns,
        "class_counts": class_counts,
    }

    # ACTUALLY SAVE
    print(f"Model saved to: {modelFilename}")
    import joblib
    joblib.dump(model_data, modelFilename)

    if debug:
        print()
        print("=== SAVE MODEL DEBUG ===")
        print(f"{modelFilename = }")
        print(f"model first tree nodes = "
            f"{model.named_steps['classifier'].estimators_[0].tree_.node_count}")
        print(f"model object id = {id(model)}")
        print(f"reference_features rows = {len(df)}")
        print(f"feature_columns = {feature_columns}")

    if debug:
        # NOW LOAD WHAT WAS ACTUALLY SAVED
        test_data = joblib.load(modelFilename)
        test_model = test_data["model"]

        print("=== SAVED MODEL DEBUG ===")
        print(f"saved model first tree nodes = "
            f"{test_model.named_steps['classifier'].estimators_[0].tree_.node_count}")
        print(f"saved model object id = {id(test_model)}")
        print(f"saved feature_columns = {test_data['feature_columns']}")

    # assert (
    #     model.named_steps['classifier'].estimators_[0].tree_.node_count
    #     == test_model.named_steps['classifier'].estimators_[0].tree_.node_count
    # )

    if debug:
        print()
        print("Saved Model metadata:")
        print(f"{feature_columns = }")
        print(f"{class_counts = }\n")

# ============================================================
# Parse Arguments
# ============================================================
def parseArguments(argv):
    """
    Parse command-line arguments.
    Supported commands:
        train  [trainRate]
        detect 
        build
        predict newLaunchKmlFilename
    Returns:
        command, trainRate, filename
    """

    if len(argv) < 2:
        usage()
        return None, None, None

    command = argv[1].lower()
    trainRate = None
    filename = None

    # Parse train rate
    def parse_train_rate(value):
        try:
            rate = float(value)
        except ValueError:
            raise ValueError(f"Invalid train rate: {value}")
        # Allow either:
        #   80
        #   80.0
        #   0.80
        if rate > 1:
            rate /= 100.0
        if not 0 < rate <= 1:
            raise ValueError(f"Train rate must be between 1 and 100%, got: {value}")
        return rate

    # TRAIN
    if command == "train":
        if len(argv) > 3:
            raise ValueError("Too many arguments for train.")

        # Default:
        #   splitMode = site+rocket
        #   splitRate = 90
        trainRate = 0.90
        if len(argv) == 3:
            trainRate = parse_train_rate(argv[2])
        return command, trainRate, filename

    # DETECT
    elif command == "detect":
        if len(argv) > 2:
            raise ValueError("Too many arguments for train.")

        # Default:
        #   splitMode = site+rocket
        #   TrainRate = 80%, 85%, 90%, 95%
        trainRate = [0.80, 0.85, 0.90, 0.95]
        return command, trainRate, filename

    # BUILD
    elif command == "build":
        if len(argv) > 2:
            raise ValueError("Too many arguments for build.")

        # Defaults:
        #   splitMode = site+rocket
        #   trainRate = 100%
        trainRate = 1.00
        return command, trainRate, filename

    # PREDICT
    elif command == "predict":
        if len(argv) > 3:
            raise ValueError("Too many arguments for predict.")

        if len(argv) < 3:
            raise ValueError("predict requires a KML filename.")

        # Defaults:
        #   splitMode = site+rocket
        #   trainRate = 100%
        if not argv[2].endswith(".kml"):
            raise ValueError(f"Invalid filename {argv[2]}.")

        filename = argv[2]
        trainRate = 1.00
        return command, trainRate, filename

    # UNKNOWN COMMAND
    else:
        raise ValueError(f"Unknown command: {command}. Use 'train', 'detect', 'build', or 'predict'.")

# ============================================================
# Main
# ============================================================
def main(debug=False):
    try:
        command, trainRate, filename = parseArguments(sys.argv)

        if debug:
            print(f"\n{command=}, site+rocket, {trainRate=}, withSite=True, Megred=True, withAngle=True, {filename=}")
            return
        
        if command:
            if command == COMMAND_PREDICT:
                newKmlPath = list(PREDICT_DIR.rglob(filename))
                if not newKmlPath or not newKmlPath[0].is_file():
                    newKmlPath = list(TEMP_DIR.rglob(filename))
                    if not newKmlPath or not newKmlPath[0].is_file():
                        newKmlPath = list(DOWNLOAD_DIR.rglob(filename))
                        if not newKmlPath or not newKmlPath[0].is_file():
                            raise ValueError(f"Not found file: '{filename}'")

                model_params = myConfig.readConfig(section="MACHINE LEARNING", key="RandomForest", returnList=True, seperator="|")
                if model_params[0] == "1":
                    myExcept.run_function("RF IoU Binary runtime", predict_iou_feature_binary_new, newKmlPath[0], model=MODEL_RADNOM_FOREST)
                    myExcept.run_function("RF GEO Binary runtime", predict_geo_feature_binary_new, newKmlPath[0], model=MODEL_RADNOM_FOREST)
                    myExcept.run_function("RF GEO Classes runtime", predict_geo_feature_classes_new, newKmlPath[0], model=MODEL_RADNOM_FOREST)

                model_params = myConfig.readConfig(section="MACHINE LEARNING", key="ExtraTrees", returnList=True, seperator="|")
                if model_params[0] == "1":
                    myExcept.run_function("ET IoU Binary runtime", predict_iou_feature_binary_new, newKmlPath[0], model=MODEL_EXTRA_TREES)
                    myExcept.run_function("ET GEO Binary runtime", predict_geo_feature_binary_new, newKmlPath[0], model=MODEL_EXTRA_TREES)
                    myExcept.run_function("ET GEO Classes runtime", predict_geo_feature_classes_new, newKmlPath[0], model=MODEL_EXTRA_TREES)

                model_params = myConfig.readConfig(section="MACHINE LEARNING", key="GradientBoosting", returnList=True, seperator="|")
                if model_params[0] == "1":
                    myExcept.run_function("GB IoU Binary runtime", predict_iou_feature_binary_new, newKmlPath[0], model=MODEL_GRADIENT_BOOSTING)
                    myExcept.run_function("GB GEO Binary runtime", predict_geo_feature_binary_new, newKmlPath[0], model=MODEL_GRADIENT_BOOSTING)
                    myExcept.run_function("GB GEO Classes runtime", predict_geo_feature_classes_new, newKmlPath[0], model=MODEL_GRADIENT_BOOSTING)

                model_params = myConfig.readConfig(section="MACHINE LEARNING", key="HistGradientBoosting", returnList=True, seperator="|")
                if model_params[0] == "1":
                    myExcept.run_function("HGB IoU Binary runtime", predict_iou_feature_binary_new, newKmlPath[0], model=MODEL_HIST_GRADIENT_BOOSTING)
                    myExcept.run_function("HGB GEO Binary runtime", predict_geo_feature_binary_new, newKmlPath[0], model=MODEL_HIST_GRADIENT_BOOSTING)
                    myExcept.run_function("HGB GEO Classes runtime", predict_geo_feature_classes_new, newKmlPath[0], model=MODEL_HIST_GRADIENT_BOOSTING)

            else:
                iou_df, new_iou_rows, geo_df, new_geo_rows, geo_site_rocket_df = build_feature_database(KMLS_DIR)

                geo_duplicates = geo_df.loc[(geo_df["target"] == 1) & geo_df[["site", "file"]].duplicated(keep=False)]
                if not geo_duplicates.empty:
                    print("\nGEO Duplicated samples")
                    print(geo_duplicates)

                iou_duplicates = iou_df.loc[(iou_df["target"] == 1) & iou_df[["file1", "file2"]].duplicated(keep=False)]
                if not iou_duplicates.empty:
                    print("\nIoU Duplicated samples")
                    print(iou_duplicates)
            
                if command == COMMAND_TRAIN:
                    train_test_model(geo_df, iou_df, trainRate)
                elif command == COMMAND_DETECT:
                    detect_new_rocket_pattern(geo_df)
                elif command == COMMAND_BUILD:
                    build_prod_model(iou_df, new_iou_rows, geo_df, new_geo_rows, geo_site_rocket_df)

    except Exception:
        myExcept.printExceptionTrace()
        usage()

# ============================================================
# Print Usage
# ============================================================
def usage():
    print(
        "Usage:\n"
        "  python ml.py train [trainRate]\n"
        "  python ml.py detect\n"
        "  python ml.py build\n"
        "  python ml.py predict newLaunchKmlFilename"
    )

################################################################################################
def showRunTime(func):
    result = timeit(func, number=1, globals=globals())
    print(f'\nFinished in {timedelta(seconds=result)}\n')

################################################################################################
if __name__ == "__main__":
    showRunTime("main()")

