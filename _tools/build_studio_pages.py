#!/usr/bin/env python3
"""Builds the studio's own legal pages: privacy.html / terms.html (English) and privacy-ko.html,
terms-ja.html, ... for the other languages. They cover this website and contacting the studio, and link to
each app's own pages (one-wish-willow-*.html, wish-hertz-*.html, toolbelt-*.html), which are generated from each app's repo.

The folder starts with "_" so GitHub Pages does not publish it.
Usage: python3 _tools/build_studio_pages.py      (writes into the repository root)
"""
import html, os, re

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = "2026-10-18"
EMAIL = "sukiappstudio@gmail.com"
APPS = [("One Wish Willow", "one-wish-willow-"), ("Wish Hertz", "wish-hertz-"), ("Toolbelt", "toolbelt-"), ("Docwell", "docwell-"), ("Trail Kit", "trail-kit-"), ("Lotto Sage", "lotto-sage-"), ("Tide & Bite", "tide-and-bite-"), ("Pixel Press", "pixel-press-"), ("Pick Party", "pick-party-"), ("Fate Compass", "fate-compass-"), ("Saju Note", "saju-note-"), ("Mystic Lens", "mystic-lens-"), ("Lantern Tarot", "lantern-tarot-"), ("Slide 2048", "slide-2048-"), ("Endless Block Puzzle", "block-blast-endless-"), ("Water Sort Puzzle", "water-sort-puzzle-"), ("Mahjong Garden", "mahjong-solitaire-"), ("Classic Solitaire Collection", "classic-solitaire-"), ("Sudoku Classic", "sudoku-classic-"), ("Block Sudoku", "block-sudoku-"), ("Triple Tile Match", "triple-tile-match-")]
LANGS = [("en", "English"), ("ko", "한국어"), ("ja", "日本語"), ("pt", "Português (Brasil)"), ("ru", "Русский"),
         ("de", "Deutsch"), ("hi", "हिन्दी"), ("vi", "Tiếng Việt"), ("fr", "Français")]
FOOTER = """<footer lang="en">
  <div class="wrap">
    Republic of Korea<br>
    Business Registration Number: 505-39-62156<br>
    <a href="mailto:sukiappstudio@gmail.com">sukiappstudio@gmail.com</a><br>
    © 2026 Suki App Studio. All rights reserved.
  </div>
</footer>"""

# "{{APPS}}" on its own line becomes the list of the apps' own pages for the same document and language.
TEXT = {
"privacy": {
"en": """# Privacy Policy
Effective date: {{DATE}}
Suki App Studio ("we", "us") is an independent app studio in the Republic of Korea. This policy covers this website (sukiappstudio.github.io) and messages you send us. Each of our apps has its own privacy policy, which explains what that app processes:
{{APPS}}
## 1. This website
The website has no accounts, forms, cookies, analytics or advertising, and we do not collect personal information through it.
It is hosted on GitHub Pages (GitHub, Inc., USA), which may log technical data such as your IP address to deliver and protect the service: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
Its fonts are loaded from Google Fonts (Google LLC, USA), which receives your IP address and browser information when a page loads: https://policies.google.com/privacy
## 2. When you contact us
If you email us, we receive your email address, your message and anything you attach. We use them only to reply and to handle your request, and we delete them once the matter is closed, unless the law requires us to keep them longer. Our email is provided by Gmail (Google LLC).
## 3. Sharing
We do not sell personal information and we do not share it with anyone, except where the law requires it.
## 4. Your rights
You can ask us to access, correct or delete the messages you sent us, and you may lodge a complaint with your data protection authority.
## 5. Children
This website is not directed at children under 14.
## 6. Changes
If we change this policy, we will publish the new version on this page with a new effective date.
## 7. Contact
Suki App Studio, Republic of Korea. Email: {{EMAIL}}""",
"ko": """# 개인정보처리방침
시행일: {{DATE}}
Suki App Studio(이하 "저희")는 대한민국의 독립 앱 스튜디오입니다. 이 방침은 이 웹사이트(sukiappstudio.github.io)와 저희에게 보내는 문의에 적용됩니다. 각 앱이 처리하는 정보는 앱마다 따로 마련한 개인정보처리방침에서 안내합니다.
{{APPS}}
## 1. 이 웹사이트
이 웹사이트에는 회원가입, 입력 양식, 쿠키, 분석 도구, 광고가 없으며, 저희는 웹사이트를 통해 개인정보를 수집하지 않습니다.
웹사이트는 GitHub Pages(GitHub, Inc., 미국)에서 호스팅되며, GitHub는 서비스 제공과 보안을 위해 IP 주소 등 기술 정보를 기록할 수 있습니다: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
글꼴은 Google Fonts(Google LLC, 미국)에서 불러오며, 페이지를 열 때 IP 주소와 브라우저 정보가 Google에 전달됩니다: https://policies.google.com/privacy
## 2. 문의하실 때
이메일로 문의하시면 이메일 주소, 문의 내용, 첨부 파일을 받게 됩니다. 이 정보는 답변과 요청 처리에만 쓰며, 처리가 끝나면 지체 없이 파기합니다. 다만 법령에 따라 보관해야 하는 경우에는 그 기간 동안 보관합니다. 이메일은 Gmail(Google LLC)을 이용합니다.
## 3. 제공
저희는 개인정보를 판매하지 않으며, 법령에 따른 경우를 제외하고 누구에게도 제공하지 않습니다.
## 4. 이용자의 권리
보내신 문의 내용의 열람, 정정, 삭제를 요청하실 수 있으며, 개인정보 보호 감독기관에 민원을 제기하실 수 있습니다.
## 5. 아동
이 웹사이트는 만 14세 미만 아동을 대상으로 하지 않습니다.
## 6. 변경
방침을 바꾸면 새 시행일과 함께 이 페이지에 게시합니다.
## 7. 연락처
Suki App Studio, 대한민국. 이메일: {{EMAIL}}""",
"ja": """# プライバシーポリシー
施行日: {{DATE}}
Suki App Studio(以下「当スタジオ」)は大韓民国の独立系アプリスタジオです。本ポリシーは、本ウェブサイト(sukiappstudio.github.io)と当スタジオへのお問い合わせに適用されます。各アプリが取り扱う情報については、アプリごとのプライバシーポリシーをご覧ください。
{{APPS}}
## 1. 本ウェブサイト
本ウェブサイトには、アカウント、入力フォーム、Cookie、アクセス解析、広告はなく、当スタジオが本ウェブサイトを通じて個人情報を収集することはありません。
本ウェブサイトは GitHub Pages(GitHub, Inc.、米国)でホスティングされており、GitHub はサービスの提供と保護のために IP アドレスなどの技術情報を記録することがあります: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
フォントは Google Fonts(Google LLC、米国)から読み込まれ、ページを開くと IP アドレスとブラウザ情報が Google に送信されます: https://policies.google.com/privacy
## 2. お問い合わせの際
メールでお問い合わせいただくと、メールアドレス、お問い合わせ内容、添付ファイルを受け取ります。これらは返信とご依頼への対応にのみ使用し、対応が完了したら削除します。ただし法令により保存が必要な場合はその期間保存します。メールには Gmail(Google LLC)を利用しています。
## 3. 第三者提供
当スタジオは個人情報を販売せず、法令に基づく場合を除き第三者に提供しません。
## 4. お客様の権利
送信されたお問い合わせ内容の開示、訂正、削除を請求でき、データ保護当局に苦情を申し立てることができます。
## 5. 子ども
本ウェブサイトは14歳未満の子どもを対象としていません。
## 6. 変更
本ポリシーを変更する場合は、新しい施行日とともにこのページで公開します。
## 7. お問い合わせ先
Suki App Studio、大韓民国。メール: {{EMAIL}}""",
"pt": """# Política de Privacidade
Data de vigência: {{DATE}}
A Suki App Studio ("nós") é um estúdio independente de aplicativos na República da Coreia. Esta política abrange este site (sukiappstudio.github.io) e as mensagens que você nos envia. Cada um dos nossos aplicativos tem sua própria política de privacidade, que explica o que o aplicativo trata:
{{APPS}}
## 1. Este site
O site não tem contas, formulários, cookies, ferramentas de análise nem publicidade, e não coletamos dados pessoais por meio dele.
Ele é hospedado no GitHub Pages (GitHub, Inc., EUA), que pode registrar dados técnicos, como o seu endereço IP, para fornecer e proteger o serviço: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
As fontes são carregadas do Google Fonts (Google LLC, EUA), que recebe o seu endereço IP e informações do navegador quando uma página é aberta: https://policies.google.com/privacy
## 2. Quando você entra em contato
Se você nos enviar um e-mail, recebemos o seu endereço de e-mail, a sua mensagem e os anexos. Usamos esses dados apenas para responder e atender ao seu pedido, e os excluímos quando o assunto é encerrado, salvo se a lei exigir que os guardemos por mais tempo. Nosso e-mail é fornecido pelo Gmail (Google LLC).
## 3. Compartilhamento
Não vendemos dados pessoais e não os compartilhamos com ninguém, exceto quando a lei exigir.
## 4. Seus direitos
Você pode pedir acesso, correção ou exclusão das mensagens que nos enviou e pode apresentar reclamação à autoridade de proteção de dados (no Brasil, a ANPD).
## 5. Crianças
Este site não é direcionado a menores de 14 anos.
## 6. Alterações
Se alterarmos esta política, publicaremos a nova versão nesta página com uma nova data de vigência.
## 7. Contato
Suki App Studio, República da Coreia. E-mail: {{EMAIL}}""",
"ru": """# Политика конфиденциальности
Дата вступления в силу: {{DATE}}
Suki App Studio («мы») — независимая студия приложений в Республике Корея. Эта политика относится к этому сайту (sukiappstudio.github.io) и к сообщениям, которые вы нам отправляете. У каждого нашего приложения есть своя политика конфиденциальности, в которой описано, какие данные оно обрабатывает:
{{APPS}}
## 1. Этот сайт
На сайте нет учётных записей, форм, файлов cookie, аналитики и рекламы, и мы не собираем через него персональные данные.
Сайт размещён на GitHub Pages (GitHub, Inc., США), который может записывать технические данные, например ваш IP-адрес, чтобы предоставлять и защищать сервис: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
Шрифты загружаются из Google Fonts (Google LLC, США), который при открытии страницы получает ваш IP-адрес и сведения о браузере: https://policies.google.com/privacy
## 2. Когда вы пишете нам
Если вы пишете нам по электронной почте, мы получаем ваш адрес, сообщение и вложения. Мы используем их только для ответа и выполнения вашего запроса и удаляем после того, как вопрос решён, если закон не требует хранить их дольше. Наша почта работает на Gmail (Google LLC).
## 3. Передача данных
Мы не продаём персональные данные и никому их не передаём, кроме случаев, предусмотренных законом.
## 4. Ваши права
Вы можете запросить доступ к отправленным нам сообщениям, их исправление или удаление, а также подать жалобу в орган по защите данных.
## 5. Дети
Этот сайт не предназначен для детей младше 14 лет.
## 6. Изменения
Если мы изменим эту политику, мы опубликуем новую версию на этой странице с новой датой вступления в силу.
## 7. Контакты
Suki App Studio, Республика Корея. Эл. почта: {{EMAIL}}""",
"de": """# Datenschutzerklärung
Gültig ab: {{DATE}}
Suki App Studio („wir“) ist ein unabhängiges App-Studio in der Republik Korea. Diese Erklärung gilt für diese Website (sukiappstudio.github.io) und für Nachrichten, die Sie uns senden. Jede unserer Apps hat eine eigene Datenschutzerklärung, die erklärt, was die App verarbeitet:
{{APPS}}
## 1. Diese Website
Die Website hat keine Konten, Formulare, Cookies, Analysewerkzeuge oder Werbung, und wir erheben über sie keine personenbezogenen Daten.
Sie wird auf GitHub Pages (GitHub, Inc., USA) gehostet; GitHub kann technische Daten wie Ihre IP-Adresse protokollieren, um den Dienst bereitzustellen und zu schützen: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
Die Schriftarten werden von Google Fonts (Google LLC, USA) geladen; Google erhält beim Laden einer Seite Ihre IP-Adresse und Browserinformationen: https://policies.google.com/privacy
## 2. Wenn Sie uns kontaktieren
Wenn Sie uns eine E-Mail senden, erhalten wir Ihre E-Mail-Adresse, Ihre Nachricht und Anhänge. Wir verwenden sie nur, um zu antworten und Ihr Anliegen zu bearbeiten, und löschen sie, sobald es erledigt ist, sofern das Gesetz keine längere Aufbewahrung verlangt. Unsere E-Mail läuft über Gmail (Google LLC).
## 3. Weitergabe
Wir verkaufen keine personenbezogenen Daten und geben sie an niemanden weiter, außer wenn das Gesetz es verlangt.
## 4. Ihre Rechte
Sie können Auskunft über die Nachrichten, die Sie uns gesendet haben, sowie deren Berichtigung oder Löschung verlangen und sich bei einer Datenschutzaufsichtsbehörde beschweren.
## 5. Kinder
Diese Website richtet sich nicht an Kinder unter 14 Jahren.
## 6. Änderungen
Wenn wir diese Erklärung ändern, veröffentlichen wir die neue Fassung auf dieser Seite mit einem neuen Gültigkeitsdatum.
## 7. Kontakt
Suki App Studio, Republik Korea. E-Mail: {{EMAIL}}""",
"hi": """# गोपनीयता नीति
प्रभावी तिथि: {{DATE}}
Suki App Studio ("हम") कोरिया गणराज्य का एक स्वतंत्र ऐप स्टूडियो है। यह नीति इस वेबसाइट (sukiappstudio.github.io) और आपके द्वारा हमें भेजे गए संदेशों पर लागू होती है। हमारे हर ऐप की अपनी गोपनीयता नीति है, जो बताती है कि वह ऐप किस जानकारी को संसाधित करता है:
{{APPS}}
## 1. यह वेबसाइट
इस वेबसाइट पर कोई खाता, फ़ॉर्म, कुकी, एनालिटिक्स या विज्ञापन नहीं है, और हम इसके माध्यम से कोई व्यक्तिगत जानकारी एकत्र नहीं करते।
यह GitHub Pages (GitHub, Inc., अमेरिका) पर होस्ट की जाती है, जो सेवा देने और उसकी सुरक्षा के लिए आपके IP पते जैसी तकनीकी जानकारी दर्ज कर सकता है: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
इसके फ़ॉन्ट Google Fonts (Google LLC, अमेरिका) से लोड होते हैं, जिसे पेज खुलने पर आपका IP पता और ब्राउज़र की जानकारी मिलती है: https://policies.google.com/privacy
## 2. जब आप हमसे संपर्क करते हैं
अगर आप हमें ईमेल करते हैं, तो हमें आपका ईमेल पता, संदेश और संलग्न फ़ाइलें मिलती हैं। हम इनका उपयोग केवल जवाब देने और आपके अनुरोध को पूरा करने के लिए करते हैं, और मामला पूरा होने पर इन्हें हटा देते हैं, जब तक कि क़ानून इन्हें अधिक समय तक रखने की माँग न करे। हमारी ईमेल सेवा Gmail (Google LLC) है।
## 3. साझा करना
हम व्यक्तिगत जानकारी नहीं बेचते और क़ानूनी आवश्यकता के अलावा इसे किसी के साथ साझा नहीं करते।
## 4. आपके अधिकार
आप हमें भेजे गए संदेशों तक पहुँच, उनमें सुधार या उन्हें हटाने का अनुरोध कर सकते हैं, और डेटा संरक्षण प्राधिकरण से शिकायत कर सकते हैं।
## 5. बच्चे
यह वेबसाइट 14 वर्ष से कम आयु के बच्चों के लिए नहीं है।
## 6. बदलाव
अगर हम यह नीति बदलते हैं, तो नई प्रभावी तिथि के साथ नया संस्करण इसी पेज पर प्रकाशित करेंगे।
## 7. संपर्क
Suki App Studio, कोरिया गणराज्य। ईमेल: {{EMAIL}}""",
"vi": """# Chính sách quyền riêng tư
Ngày hiệu lực: {{DATE}}
Suki App Studio ("chúng tôi") là một studio ứng dụng độc lập tại Hàn Quốc. Chính sách này áp dụng cho trang web này (sukiappstudio.github.io) và các tin nhắn bạn gửi cho chúng tôi. Mỗi ứng dụng của chúng tôi có chính sách quyền riêng tư riêng, giải thích ứng dụng đó xử lý những gì:
{{APPS}}
## 1. Trang web này
Trang web không có tài khoản, biểu mẫu, cookie, công cụ phân tích hay quảng cáo, và chúng tôi không thu thập thông tin cá nhân qua trang web.
Trang web được lưu trữ trên GitHub Pages (GitHub, Inc., Hoa Kỳ), nơi có thể ghi lại dữ liệu kỹ thuật như địa chỉ IP của bạn để cung cấp và bảo vệ dịch vụ: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
Phông chữ được tải từ Google Fonts (Google LLC, Hoa Kỳ), nơi nhận địa chỉ IP và thông tin trình duyệt của bạn khi trang được mở: https://policies.google.com/privacy
## 2. Khi bạn liên hệ với chúng tôi
Nếu bạn gửi email, chúng tôi nhận được địa chỉ email, nội dung tin nhắn và tệp đính kèm của bạn. Chúng tôi chỉ dùng chúng để trả lời và xử lý yêu cầu của bạn, và xóa chúng khi sự việc kết thúc, trừ khi pháp luật yêu cầu lưu giữ lâu hơn. Email của chúng tôi do Gmail (Google LLC) cung cấp.
## 3. Chia sẻ
Chúng tôi không bán thông tin cá nhân và không chia sẻ với bất kỳ ai, trừ khi pháp luật yêu cầu.
## 4. Quyền của bạn
Bạn có thể yêu cầu truy cập, chỉnh sửa hoặc xóa các tin nhắn đã gửi cho chúng tôi, và có thể khiếu nại với cơ quan bảo vệ dữ liệu.
## 5. Trẻ em
Trang web này không dành cho trẻ em dưới 14 tuổi.
## 6. Thay đổi
Nếu thay đổi chính sách này, chúng tôi sẽ đăng phiên bản mới trên trang này kèm ngày hiệu lực mới.
## 7. Liên hệ
Suki App Studio, Hàn Quốc. Email: {{EMAIL}}""",
"fr": """# Politique de confidentialité
Date d'entrée en vigueur : {{DATE}}
Suki App Studio (« nous ») est un studio d'applications indépendant établi en République de Corée. Cette politique s'applique à ce site (sukiappstudio.github.io) et aux messages que vous nous envoyez. Chacune de nos applications a sa propre politique de confidentialité, qui explique ce que l'application traite :
{{APPS}}
## 1. Ce site
Le site n'a ni comptes, ni formulaires, ni cookies, ni outils de mesure d'audience, ni publicité, et nous ne collectons aucune donnée personnelle par son intermédiaire.
Il est hébergé sur GitHub Pages (GitHub, Inc., États-Unis), qui peut enregistrer des données techniques comme votre adresse IP pour fournir et protéger le service : https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement
Les polices sont chargées depuis Google Fonts (Google LLC, États-Unis), qui reçoit votre adresse IP et des informations sur votre navigateur à l'ouverture d'une page : https://policies.google.com/privacy
## 2. Lorsque vous nous contactez
Si vous nous écrivez par e-mail, nous recevons votre adresse e-mail, votre message et les pièces jointes. Nous les utilisons uniquement pour vous répondre et traiter votre demande, et nous les supprimons une fois la demande close, sauf si la loi exige une conservation plus longue. Notre messagerie est fournie par Gmail (Google LLC).
## 3. Partage
Nous ne vendons pas de données personnelles et ne les partageons avec personne, sauf lorsque la loi l'exige.
## 4. Vos droits
Vous pouvez demander l'accès aux messages que vous nous avez envoyés, leur rectification ou leur suppression, et introduire une réclamation auprès de votre autorité de protection des données (en France, la CNIL).
## 5. Enfants
Ce site ne s'adresse pas aux enfants de moins de 14 ans.
## 6. Modifications
Si nous modifions cette politique, nous publierons la nouvelle version sur cette page avec une nouvelle date d'entrée en vigueur.
## 7. Contact
Suki App Studio, République de Corée. E-mail : {{EMAIL}}""",
},
"terms": {
"en": """# Terms of Use
Effective date: {{DATE}}
These terms apply to this website (sukiappstudio.github.io), operated by Suki App Studio. Each of our apps has its own terms of service:
{{APPS}}
## 1. Using the website
The website gives information about Suki App Studio and its apps. You may read it and link to it freely.
## 2. Intellectual property
The text, names, logos and images on this website belong to Suki App Studio or its licensors. Please do not copy or reuse them beyond personal, non-commercial use without our permission.
## 3. No warranty
The website is provided "as is". We try to keep it accurate and available, but we do not guarantee that it is complete, current or always online. Links to other websites are provided for convenience, and we are not responsible for their content.
## 4. Limitation of liability
To the extent permitted by law, Suki App Studio is not liable for damages arising from the use of this website. Nothing in these terms limits rights you have under mandatory consumer protection law.
## 5. Governing law
These terms are governed by the laws of the Republic of Korea, without prejudice to mandatory rules of the country where you live.
## 6. Changes
We may update these terms; the new version applies from the effective date shown on this page.
## 7. Contact
Suki App Studio, Republic of Korea. Email: {{EMAIL}}""",
"ko": """# 이용약관
시행일: {{DATE}}
이 약관은 Suki App Studio가 운영하는 이 웹사이트(sukiappstudio.github.io)에 적용됩니다. 각 앱의 이용약관은 앱마다 따로 있습니다.
{{APPS}}
## 1. 웹사이트 이용
이 웹사이트는 Suki App Studio와 앱에 관한 정보를 제공합니다. 누구나 자유롭게 읽고 링크할 수 있습니다.
## 2. 지식재산권
이 웹사이트의 글, 이름, 로고, 이미지는 Suki App Studio 또는 정당한 권리자에게 있습니다. 개인적·비상업적 이용을 넘어 복제하거나 재사용하려면 저희의 허락을 받아야 합니다.
## 3. 보증의 부인
웹사이트는 "있는 그대로" 제공됩니다. 정확하고 접속 가능한 상태를 유지하려 노력하지만, 내용이 완전하거나 최신이거나 항상 접속된다고 보증하지 않습니다. 다른 웹사이트로의 링크는 편의를 위해 제공하며, 그 내용에 대해 책임지지 않습니다.
## 4. 책임의 제한
법령이 허용하는 범위에서 Suki App Studio는 이 웹사이트 이용으로 발생한 손해에 대해 책임지지 않습니다. 이 약관은 강행 소비자보호법상 이용자의 권리를 제한하지 않습니다.
## 5. 준거법
이 약관에는 대한민국 법이 적용됩니다. 다만 이용자가 거주하는 국가의 강행규정은 그대로 적용됩니다.
## 6. 변경
약관을 바꿀 수 있으며, 새 약관은 이 페이지에 표시된 시행일부터 적용됩니다.
## 7. 연락처
Suki App Studio, 대한민국. 이메일: {{EMAIL}}""",
"ja": """# 利用規約
施行日: {{DATE}}
本規約は、Suki App Studio が運営する本ウェブサイト(sukiappstudio.github.io)に適用されます。各アプリの利用規約はアプリごとに定めています。
{{APPS}}
## 1. ウェブサイトの利用
本ウェブサイトは Suki App Studio とそのアプリに関する情報を提供します。自由に閲覧し、リンクしていただけます。
## 2. 知的財産
本ウェブサイトの文章、名称、ロゴ、画像は Suki App Studio またはその権利者に帰属します。個人的かつ非商業的な利用の範囲を超えて複製・再利用する場合は、当スタジオの許可が必要です。
## 3. 保証の否認
本ウェブサイトは「現状のまま」提供されます。正確で利用可能な状態を保つよう努めますが、内容の完全性、最新性、常時利用可能であることを保証しません。他のウェブサイトへのリンクは便宜のためのものであり、その内容について責任を負いません。
## 4. 責任の制限
法令で認められる範囲で、Suki App Studio は本ウェブサイトの利用により生じた損害について責任を負いません。本規約は、強行法規である消費者保護法に基づくお客様の権利を制限するものではありません。
## 5. 準拠法
本規約は大韓民国法に準拠します。ただし、お客様の居住国の強行規定の適用を妨げません。
## 6. 変更
本規約は変更されることがあり、新しい規約はこのページに記載の施行日から適用されます。
## 7. お問い合わせ先
Suki App Studio、大韓民国。メール: {{EMAIL}}""",
"pt": """# Termos de Uso
Data de vigência: {{DATE}}
Estes termos se aplicam a este site (sukiappstudio.github.io), operado pela Suki App Studio. Cada um dos nossos aplicativos tem seus próprios termos de serviço:
{{APPS}}
## 1. Uso do site
O site traz informações sobre a Suki App Studio e seus aplicativos. Você pode lê-lo e criar links para ele livremente.
## 2. Propriedade intelectual
Os textos, nomes, logotipos e imagens deste site pertencem à Suki App Studio ou aos seus licenciantes. Não os copie nem reutilize além do uso pessoal e não comercial sem a nossa autorização.
## 3. Sem garantia
O site é fornecido "no estado em que se encontra". Procuramos mantê-lo correto e disponível, mas não garantimos que esteja completo, atualizado ou sempre no ar. Os links para outros sites são oferecidos por conveniência, e não somos responsáveis pelo conteúdo deles.
## 4. Limitação de responsabilidade
Na medida permitida por lei, a Suki App Studio não se responsabiliza por danos decorrentes do uso deste site. Nada nestes termos limita os direitos que você tem pelo Código de Defesa do Consumidor ou outra lei obrigatória.
## 5. Lei aplicável
Estes termos são regidos pelas leis da República da Coreia, sem prejuízo das normas obrigatórias do país onde você mora.
## 6. Alterações
Podemos atualizar estes termos; a nova versão vale a partir da data de vigência indicada nesta página.
## 7. Contato
Suki App Studio, República da Coreia. E-mail: {{EMAIL}}""",
"ru": """# Условия использования
Дата вступления в силу: {{DATE}}
Эти условия относятся к этому сайту (sukiappstudio.github.io), которым управляет Suki App Studio. У каждого нашего приложения есть свои условия использования:
{{APPS}}
## 1. Использование сайта
Сайт содержит информацию о Suki App Studio и её приложениях. Вы можете свободно читать его и ссылаться на него.
## 2. Интеллектуальная собственность
Тексты, названия, логотипы и изображения на этом сайте принадлежат Suki App Studio или её лицензиарам. Не копируйте и не используйте их сверх личного некоммерческого использования без нашего разрешения.
## 3. Отказ от гарантий
Сайт предоставляется «как есть». Мы стараемся поддерживать его точным и доступным, но не гарантируем, что он полон, актуален или всегда работает. Ссылки на другие сайты даются для удобства, и мы не отвечаем за их содержание.
## 4. Ограничение ответственности
В пределах, допускаемых законом, Suki App Studio не несёт ответственности за ущерб, возникший в связи с использованием этого сайта. Ничто в этих условиях не ограничивает ваши права по обязательному законодательству о защите прав потребителей.
## 5. Применимое право
Эти условия регулируются законодательством Республики Корея без ущерба для обязательных норм страны вашего проживания.
## 6. Изменения
Мы можем обновлять эти условия; новая редакция действует с даты, указанной на этой странице.
## 7. Контакты
Suki App Studio, Республика Корея. Эл. почта: {{EMAIL}}""",
"de": """# Nutzungsbedingungen
Gültig ab: {{DATE}}
Diese Bedingungen gelten für diese Website (sukiappstudio.github.io), die von Suki App Studio betrieben wird. Jede unserer Apps hat eigene Nutzungsbedingungen:
{{APPS}}
## 1. Nutzung der Website
Die Website informiert über Suki App Studio und seine Apps. Sie dürfen sie frei lesen und auf sie verlinken.
## 2. Geistiges Eigentum
Texte, Namen, Logos und Bilder auf dieser Website gehören Suki App Studio oder seinen Lizenzgebern. Bitte kopieren oder verwenden Sie sie über die private, nicht kommerzielle Nutzung hinaus nicht ohne unsere Erlaubnis.
## 3. Keine Gewährleistung
Die Website wird „wie besehen“ bereitgestellt. Wir bemühen uns, sie richtig und erreichbar zu halten, garantieren aber nicht, dass sie vollständig, aktuell oder jederzeit verfügbar ist. Links auf andere Websites dienen der Bequemlichkeit; für deren Inhalte sind wir nicht verantwortlich.
## 4. Haftungsbeschränkung
Soweit gesetzlich zulässig, haftet Suki App Studio nicht für Schäden aus der Nutzung dieser Website. Die Haftung für Vorsatz, grobe Fahrlässigkeit und Verletzung von Leben, Körper oder Gesundheit sowie Ihre Rechte aus zwingendem Verbraucherschutzrecht bleiben unberührt.
## 5. Anwendbares Recht
Für diese Bedingungen gilt das Recht der Republik Korea; zwingende Vorschriften des Landes, in dem Sie leben, bleiben unberührt.
## 6. Änderungen
Wir können diese Bedingungen aktualisieren; die neue Fassung gilt ab dem auf dieser Seite angegebenen Datum.
## 7. Kontakt
Suki App Studio, Republik Korea. E-Mail: {{EMAIL}}""",
"hi": """# उपयोग की शर्तें
प्रभावी तिथि: {{DATE}}
ये शर्तें Suki App Studio द्वारा संचालित इस वेबसाइट (sukiappstudio.github.io) पर लागू होती हैं। हमारे हर ऐप की अपनी सेवा की शर्तें हैं:
{{APPS}}
## 1. वेबसाइट का उपयोग
यह वेबसाइट Suki App Studio और उसके ऐप्स के बारे में जानकारी देती है। आप इसे स्वतंत्र रूप से पढ़ सकते हैं और इसका लिंक दे सकते हैं।
## 2. बौद्धिक संपदा
इस वेबसाइट के पाठ, नाम, लोगो और चित्र Suki App Studio या उसके लाइसेंसदाताओं के हैं। व्यक्तिगत, गैर-व्यावसायिक उपयोग से आगे हमारी अनुमति के बिना इनकी नकल या पुनः उपयोग न करें।
## 3. कोई वारंटी नहीं
वेबसाइट "जैसी है" उपलब्ध कराई जाती है। हम इसे सही और उपलब्ध रखने का प्रयास करते हैं, लेकिन यह गारंटी नहीं देते कि यह पूर्ण, अद्यतन या हमेशा ऑनलाइन रहेगी। अन्य वेबसाइटों के लिंक सुविधा के लिए दिए गए हैं, और उनकी सामग्री के लिए हम ज़िम्मेदार नहीं हैं।
## 4. दायित्व की सीमा
क़ानून द्वारा अनुमत सीमा तक, Suki App Studio इस वेबसाइट के उपयोग से होने वाली किसी भी हानि के लिए उत्तरदायी नहीं है। ये शर्तें अनिवार्य उपभोक्ता संरक्षण क़ानून के तहत आपके अधिकारों को सीमित नहीं करतीं।
## 5. लागू क़ानून
ये शर्तें कोरिया गणराज्य के क़ानूनों द्वारा शासित हैं, और आपके निवास वाले देश के अनिवार्य नियम भी लागू रहते हैं।
## 6. बदलाव
हम इन शर्तों को अपडेट कर सकते हैं; नया संस्करण इस पेज पर दिखाई गई प्रभावी तिथि से लागू होगा।
## 7. संपर्क
Suki App Studio, कोरिया गणराज्य। ईमेल: {{EMAIL}}""",
"vi": """# Điều khoản sử dụng
Ngày hiệu lực: {{DATE}}
Các điều khoản này áp dụng cho trang web này (sukiappstudio.github.io) do Suki App Studio vận hành. Mỗi ứng dụng của chúng tôi có điều khoản dịch vụ riêng:
{{APPS}}
## 1. Sử dụng trang web
Trang web cung cấp thông tin về Suki App Studio và các ứng dụng của studio. Bạn có thể tự do đọc và liên kết đến trang web.
## 2. Sở hữu trí tuệ
Văn bản, tên, logo và hình ảnh trên trang web này thuộc về Suki App Studio hoặc bên cấp phép. Vui lòng không sao chép hay sử dụng lại vượt quá mục đích cá nhân, phi thương mại khi chưa có sự cho phép của chúng tôi.
## 3. Không bảo đảm
Trang web được cung cấp "nguyên trạng". Chúng tôi cố gắng giữ trang web chính xác và truy cập được, nhưng không bảo đảm trang web đầy đủ, cập nhật hay luôn hoạt động. Liên kết đến trang web khác chỉ nhằm thuận tiện, và chúng tôi không chịu trách nhiệm về nội dung của chúng.
## 4. Giới hạn trách nhiệm
Trong phạm vi pháp luật cho phép, Suki App Studio không chịu trách nhiệm về thiệt hại phát sinh từ việc sử dụng trang web này. Điều khoản này không hạn chế các quyền của bạn theo luật bảo vệ người tiêu dùng bắt buộc.
## 5. Luật áp dụng
Các điều khoản này chịu sự điều chỉnh của pháp luật Hàn Quốc, không ảnh hưởng đến các quy định bắt buộc của quốc gia nơi bạn sinh sống.
## 6. Thay đổi
Chúng tôi có thể cập nhật các điều khoản này; phiên bản mới có hiệu lực từ ngày ghi trên trang này.
## 7. Liên hệ
Suki App Studio, Hàn Quốc. Email: {{EMAIL}}""",
"fr": """# Conditions d'utilisation
Date d'entrée en vigueur : {{DATE}}
Ces conditions s'appliquent à ce site (sukiappstudio.github.io), exploité par Suki App Studio. Chacune de nos applications a ses propres conditions d'utilisation :
{{APPS}}
## 1. Utilisation du site
Le site présente Suki App Studio et ses applications. Vous pouvez le consulter et créer des liens vers lui librement.
## 2. Propriété intellectuelle
Les textes, noms, logos et images de ce site appartiennent à Suki App Studio ou à ses concédants. Merci de ne pas les copier ni les réutiliser au-delà d'un usage personnel et non commercial sans notre autorisation.
## 3. Absence de garantie
Le site est fourni « en l'état ». Nous nous efforçons de le garder exact et accessible, sans garantir qu'il soit complet, à jour ou toujours en ligne. Les liens vers d'autres sites sont fournis par commodité et nous ne sommes pas responsables de leur contenu.
## 4. Limitation de responsabilité
Dans la mesure permise par la loi, Suki App Studio n'est pas responsable des dommages résultant de l'utilisation de ce site. Rien dans ces conditions ne limite les droits que vous tenez des dispositions impératives de protection des consommateurs.
## 5. Droit applicable
Ces conditions sont régies par le droit de la République de Corée, sans préjudice des règles impératives du pays où vous résidez.
## 6. Modifications
Nous pouvons mettre à jour ces conditions ; la nouvelle version s'applique à partir de la date indiquée sur cette page.
## 7. Contact
Suki App Studio, République de Corée. E-mail : {{EMAIL}}""",
},
}


def filename(doc, lang, prefix=""):
    return f"{prefix}{doc}.html" if lang == "en" else f"{prefix}{doc}-{lang}.html"


def linkify(text):
    text = html.escape(text)
    text = re.sub(r"(https?://[^\s<)]+[^\s<).,])", r'<a href="\1">\1</a>', text)
    return re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+[\w])", r'<a href="mailto:\1">\1</a>', text)


for doc, texts in TEXT.items():
    for lang, _ in LANGS:
        text = texts[lang].replace("{{DATE}}", DATE).replace("{{EMAIL}}", EMAIL)
        parts, title = [], doc
        for line in text.split("\n"):
            if line == "{{APPS}}":
                parts.append("  <ul>\n" + "\n".join(
                    f'    <li><a href="{filename(doc, lang, prefix)}" lang="en">{html.escape(name)}</a></li>' for name, prefix in APPS)
                    + "\n  </ul>")
            elif line.startswith("# "):
                title = line[2:]; parts.append(f"  <h1>{html.escape(title)}</h1>")
            elif line.startswith("## "):
                parts.append(f"  <h2>{html.escape(line[3:])}</h2>")
            elif line.strip():
                parts.append(f"  <p>{linkify(line)}</p>")
        nav = "\n".join(
            f'    <li><a href="{filename(doc, l)}" lang="{l}"' + (' aria-current="page"' if l == lang else "") + f">{n}</a></li>"
            for l, n in LANGS)
        page = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | Suki App Studio</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="site.css">
</head>
<body>
<header class="bar">
  <div class="wrap">
    <a class="brand" href="./">Suki App Studio</a>
    <nav lang="en">
      <a href="./#about">About</a>
      <a href="./#contact">Contact</a>
      <a href="{filename('privacy', lang)}">Privacy Policy</a>
      <a href="{filename('terms', lang)}">Terms of Service</a>
    </nav>
  </div>
</header>
<main class="wrap doc">
  <ul class="langs">
{nav}
  </ul>
{chr(10).join(parts)}
</main>
{FOOTER}
</body>
</html>
"""
        open(os.path.join(OUT, filename(doc, lang)), "w", encoding="utf-8", newline="\n").write(page)
print("studio pages written to", OUT)
