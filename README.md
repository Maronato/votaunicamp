Vota Unicamp
============

Objetivo
--------
O Objetivo desse app é oferecer um complemento democrático às assembleias da Unicamp.

Será possível colocar para votação aberta todas as pautas colocadas nas assembleias, todos os votos serão somados e somente alunos da Unicamp poderão votar

Funcionamento
-------------
O app usa o [sistema de verificação de documentos da Unicamp][1] para verificar a matrícula de cada aluno. Esse sistema devolve o Atestado de Matrícula (como PDF) que é lido para extrair as informações do aluno (Nome, RA, RG e Curso). Essas informações são colocadas no banco de dados em conjunto com o voto de cada um. (vide [privacidade](#privacy))
Além disso, é possível criar uma conta no aplicativo para compartilhar e avaliar argumentos.

Segurança
---------
O app foi testado contra os ataques web mais comuns, não foi possível invadir o sistema dessa forma.

O sistema é seguro também contra ataques do tipo __brute force__, pois é necessário preencher um campo __captcha__ para cada voto


## <a name="privacy"></a> Privacidade

O app não guarda o RG dos usuários por questões de privacidade. Apenas os 3 primeiros e o último dígitos são guardados, no formato 000\*\*\*\*\*0.

Apenas o primeiro nome é mostrado na aba de resultados.

O RA é guardado na íntegra, porém não é mostrado aos outros usuários, sendo mascarado de forma similar ao RG, deixando visíveis apenas os 3 primeiros dígitos. Esse número é importante para garantir que um mesmo aluno não vote duas vezes e para permitir alteração do voto.

[1]: https://www.daconline.unicamp.br/ActionConsultaDiploma.asp
