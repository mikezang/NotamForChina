rem                    JOB Net名：AFLD01-NET
rem                       JOB 名：AFLD01000E
rem                               AFLD01100U
rem                               AFLD01999E
rem                 Noge Group名：NGWAFL01
rem Application 個別カレンダー名：AFL01

rem %1 = \\FKMDPWSFS01.ad01.smfl.co.jp\af_live\
rem %2 = \\FKMDPWSFS03.ad01.smfl.co.jp\af_live\
robocopy %1 %2 /S /MOVE /XD c:\zang\nodejs /XF c:\zang\mycopy.bat
