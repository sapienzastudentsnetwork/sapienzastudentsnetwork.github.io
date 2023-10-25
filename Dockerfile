FROM jekyll/minimal:pages

ENV PAGES_REPO_NWO="sapienzastudentsnetwork/informatica"

RUN apk add --no-cache make gcc libc-dev

RUN gem install webrick
RUN gem install jemoji
RUN gem install jekyll-last-modified-at

ENTRYPOINT [ "jekyll", "serve", "--force_polling", "--watch" ]
