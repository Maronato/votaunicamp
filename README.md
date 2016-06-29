Vota Unicamp
============

Objetivo
--------
O Objetivo desse app é oferecer um complemento democrático às assembleias da Unicamp.

Será possível colocar para votação aberta todas as pautas colocadas nas assembleias, todos os votos serão somados e somente alunos da Unicamp poderão votar

Funcionamento
-------------
O app usa o [sistema de verificação de documentos da Unicamp][1] para verificar a matrícula de cada aluno. Esse sistema devolve o Atestado de Matrícula (como PDF) que é lido para extrair as informações do aluno (Nome, RA e Curso). Essas informações são colocadas no banco de dados em conjunto com o voto de cada um. (vide [privacidade](#privacy))
Além disso, é possível compartilhar e avaliar argumentos e comentários sobre as pautas.

Segurança
---------
O app foi testado contra os ataques web mais comuns, não foi possível invadir o sistema dessa forma.

O sistema é seguro também contra ataques do tipo __brute force__, pois é necessário preencher um campo __captcha__ para cada voto.

Valores e preocupações
----------------------

O app toma privacidade e segurança como prioridades. Nenhuma informação além do nome, ra e curso é lida ou salva. O PDF de onde essas informações são retiradas também é deletado assim que é lido, não ficando salvo no sistema.

No desenvolvimento do aplicatico foram tomadas algumas decisões que podem ser questionadas.

Uma delas é o formato completamente anônimo dos votos. A versão anterior do aplicativo, para incentivar a confiança na disposição de apenas votos válidos, dispunha de informações como nome, ra e rg nos resultados. Isso cumpria com o propósito, mas trazia outro problema: a identificação de usuários por terceiros. Diante disso foi decidido que a segurança dos usuários e a capacidade de livremente expor seus ideais deveria estar em primeiro plano.

Infelizmente o voto anônimo e a validação do voto são características mutuamente exclusivas, portanto escolhi pela primeira.

## <a name="privacy"></a> Privacidade

O app salva apenas o Nome, RA e Curso do aluno. Nenhuma dessas informações é mostrada a outros usuários, com exceção do curso, que é mostrado na aba de resultados junto a um nome fictício gerado automaticamente.

Este nome fictício é único para cada usuário e serve para que o usuário se identifique nos comentários e resultados.

O RA é guardado na íntegra, porém não é mostrado aos outros usuários. É usado apenas para realizar o login e para garantir que um mesmo aluno não vote duas vezes.

[1]: https://www.daconline.unicamp.br/ActionConsultaDiploma.asp
