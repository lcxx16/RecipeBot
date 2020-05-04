create table inverted_index( 
  index_id serial
  , index_name varchar (30)
  , index_kana varchar (30)
  , index_category varchar(20)
  , index text
  , primary key (index_id)
);