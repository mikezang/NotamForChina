mysql -uroot <<EOF
drop table if exists master.customer;
drop table if exists master.customer_order;
drop table if exists replica.customer;
drop table if exists replica.customer_order;
drop table if exists master.some_table;
drop table if exists replica.some_table;
EOF
