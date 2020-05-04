create table public.category( 
  category char (1)
  , category_id numeric (5)
  , category_name varchar(30)
  , category_url text
  , parent_category numeric (4)
  , primary key (category, category_id)
);
