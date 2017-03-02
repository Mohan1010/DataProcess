DROP TABLE IF EXISTS `T`;
CREATE TABLE `T` (
`n` int(11)
);

INSERT INTO `T`(n) SELECT @row := @row + 1 as row FROM
(select 0 union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) t,
(select 0 union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) t2,
(select 0 union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) t3,
(select 0 union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) t4,
(select 0 union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) t5,
(select 0 union all select 1 union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9) t6,
(SELECT @row:=0) t7;

SET @d0 = "2012-01-01 00:00:00";
SET @d1 = "2030-01-01 00:00:00";

SET @date = @d0;

DROP TABLE IF EXISTS time_dimension;
CREATE TABLE `time_dimension` (
`day_key`      int      NOT NULL,
`date` date      DEFAULT NULL,
`dim_year`      smallint DEFAULT NULL,
`dim_month`      smallint DEFAULT NULL,
`dim_day`      smallint DEFAULT NULL,
`dim_week`      smallint DEFAULT NULL,
`dim_quarter`      smallint DEFAULT NULL,
`dim_weekday`      smallint DEFAULT NULL,
`dim_month_name`  char(10) DEFAULT NULL,
`dim_weekday_name` char(10) DEFAULT NULL,
`dim_hour` tinyint default NULL,
PRIMARY KEY (`day_key`)
);

INSERT INTO time_dimension (`date`, day_key,   dim_year, dim_month, dim_day, dim_week, dim_quarter, dim_weekday, dim_month_name, dim_weekday_name, dim_hour)
SELECT @date := date_add(@date, interval 1 hour) as date,
date_format(@date, "%Y%m%d%HH24") as day_key,
year(@date) as y,
month(@date) as m,
day(@date) as d,
week(@date) as w,
quarter(@date) as q,
weekday(@date)+1 as wd,
monthname(@date) as m_name,
dayname(@date) as wd_name,
hour(@date) as h
FROM T
WHERE date_add(@date, interval 1 hour) <= @d1
ORDER BY date;
