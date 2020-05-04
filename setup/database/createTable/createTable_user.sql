create table public.user ( 
  user_id char (33) not null
  , user_name varchar (20)
  , user_photo text
  , status char (1)
  , register_date numeric (8)
  , delete_date numeric (8)
  , primary key (user_id)
);

