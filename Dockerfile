FROM jekyll/minimal:pages

ENV PAGES_REPO_NWO="SapienzaInformatica/sapienzainformatica.github.io"

RUN gem install webrick
RUN gem install jemoji

ENTRYPOINT [ "jekyll", "serve", "--force_polling", "--watch" ]
