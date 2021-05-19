create database todolist;
use todolist;

CREATE TABLE todos(
    id int PRIMARY KEY,
    task varchar(80) NOT NULL,
    dueby date NOT NULL,
    status varchar(80) NOT NULL
);

CREATE TABLE users(
    userid varchar(32) PRIMARY KEY,
    access varchar(32) NOT NULL
);

INSERT INTO users VALUES('ram','read');
INSERT INTO users VALUES('prem','read');
INSERT INTO users VALUES('sudhan','write');