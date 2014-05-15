drop table if exists posts;
create table posts (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  create_at integer not null,
  update_at integer not null
);
