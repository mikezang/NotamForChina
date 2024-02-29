mysql -uroot --table  <<EOF
select 'master' as 'database', '$1' as 'table', master.$1.* from master.$1;
select 'master' as 'database', '$2' as 'table', master.$2.* from master.$2;
select 'replica' as 'database', '$1' as 'table', replica.$1.* from replica.$1;
select 'replica' as 'database', '$2' as 'table', replica.$2.* from replica.$2;
EOF
