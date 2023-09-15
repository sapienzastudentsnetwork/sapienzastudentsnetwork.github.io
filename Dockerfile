FROM jekyll/minimal:pages

ENV PAGES_REPO_NWO="sapienzastudentsnetwork/informatica"

RUN gem install webrick
RUN gem install jemoji

ENTRYPOINT [ "jekyll", "serve", "--force_polling", "--watch" ]
