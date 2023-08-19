FROM jekyll/minimal:pages

ENV PAGES_REPO_NWO="SapienzaStudentsNetwork/informatica"

RUN gem install webrick
RUN gem install jemoji

ENTRYPOINT [ "jekyll", "serve", "--force_polling", "--watch" ]
