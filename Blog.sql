BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Blog" (
	"id"	INTEGER,
	"url"	TEXT,
	"title"	TEXT,
	"date"	TEXT,
	"post"	TEXT,
	"post_html"	TEXT,
	"tags"	TEXT,
	PRIMARY KEY("id")
);

COMMIT;


SELECT title FROM Blog GROUP BY title HAVING (COUNT(title) > 1);
