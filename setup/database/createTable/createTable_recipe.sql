create table public.recipe( 
  recipe_number serial
  , recipe_id numeric (20)
  , recipe_name varchar (50)
  , recipe_url text
  , recipe_photo text
  , material text
  , large_id numeric (5)
  , medium_id numeric (5)
  , small_id numeric (5)
  , register_date numeric (8)
  , primary key (recipe_id)
);
