create table public.status( 
  user_id char (33) not null
  , register_status char (1) not null
  , list_status char (1) not null
  , recipe_status char (1) not null
  , web_status char (1) not null
  , primary key (user_id)
  , foreign key (user_id) references public.user (user_id)
);
