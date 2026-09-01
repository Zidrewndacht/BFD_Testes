-- Este arquivo popula o banco temporário criado em conftest.py.
-- Ele define o estado inicial conhecido usado pelos testes.

-- Cria dois usuários: "test" e "other".
-- "test" é o usuário principal da maioria dos testes.
-- "other" existe para permitir testes de autorização, por exemplo:
-- verificar que um usuário não pode editar o post de outro usuário.
-- As senhas não estão em texto puro: são hashes gerados pelo mecanismo de
-- senha do Flask/Werkzeug. 
INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
    ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

-- Cria um post pertencente ao usuário "test".
-- author_id = 1 corresponde ao usuário "test".
-- A expressão SQL 'test' || x'0a' || 'body' concatena strings.
-- x'0a' é o byte de quebra de linha, então o body final é "test\nbody".
-- Isso permite testar se o corpo do post é renderizado corretamente no HTML.
INSERT INTO post (title, body, author_id, created)
VALUES
    ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');