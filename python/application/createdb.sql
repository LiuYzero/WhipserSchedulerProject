

-- public.video_caption definition

-- Drop table

-- DROP TABLE public.video_caption;

CREATE TABLE public.video_caption (
	id int8 GENERATED BY DEFAULT AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	video text NULL,
	caption text NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT video_caption_pkey PRIMARY KEY (id)
);