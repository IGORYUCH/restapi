create table users (user_id bigserial PRIMARY KEY, username varchar(32) UNIQUE NOT NULL, password varchar(45) NOT NULL);
--everyone has qweqwe123 password--
INSERT INTO users VALUES(default,	'serious.man@success.com',	'md5$FjLMcCPq$fb3d25b99ae684a81dfee7678392506c');
INSERT INTO users VALUES(default,	'profitable@company.com',	'md5$xVFx4i2t$81640994f6bef1daec25b56ba38ba94a');
INSERT INTO users VALUES(default,	'grinev.igoryok@gmail.com',	'md5$PpcOAA5j$667da25aa61a5b89e9bea5919be40ef2');
INSERT INTO users VALUES(default,	'unzver@mail.ru',	'md5$KfubkY0v$d1b1eb19ba479f970d0e1c1fed61bd89');

create table tasks (task_id bigserial PRIMARY KEY, user_id bigint REFERENCES users (user_id) NOT NULL, title varchar(64) NOT NULL, description text, completed bool NOT NULL, complete_date date NOT NULL);

INSERT INTO tasks VALUES(default, 4, 'Поесть',	'еда в холодильнике', false, '2020-12-06');
INSERT INTO tasks VALUES(default, 4, 'Поспать', 'Найти кровать', false, '2020-12-07');
INSERT INTO tasks VALUES(default, 4, 'Отдохнуть', 'Посмотреть в окно', false, '2020-12-07');
INSERT INTO tasks (task_id, user_id, title, completed, complete_date) VALUES(default, 3, 'Get a job', false, '2020-12-31');
INSERT INTO tasks VALUES(default, 2, 'buy a rival',  'buy a rival''s company', false, '2020-02-01');
INSERT INTO tasks VALUES(default, 2, 'invest to AT&T', 'invest all the money', false, '2021-01-01');
INSERT INTO tasks VALUES(default, 1, 'Start a business', 'Open a fish shop', false, '2021-01-01');
