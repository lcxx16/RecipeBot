create table public.product_archive( 
  product_id serial
  , product_name varchar(15)
  , product_kana varchar(30)
  , user_id varchar (33) not null REFERENCES public.user (user_id)
  , register_date numeric (8) not null
  , expire_date numeric (8) not null
  , status char (1) not null
  , primary key (product_id)
);
