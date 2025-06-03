DROP TABLE IF EXISTS loja;

CREATE TABLE loja (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome_da_loja TEXT NOT NULL,
  nome_do_proprietario TEXT NOT NULL,
  nome_de_usuario TEXT UNIQUE NOT NULL,
  senha TEXT NOT NULL
);
