drop table if exists posts;
create table posts (
    id integer primary key autoincrement,
    title text not null,
    markdown text not null,
    content text not null,
    slug text ,
    keyword text ,
    desc text,
    create_at integer not null,
    update_at integer not null
);

drop table if exists categories;
create table categories (
    id integer primary key autoincrement,
    name text not null,
    desc text not null,
    create_at integer not null,
    update_at integer not null
);
