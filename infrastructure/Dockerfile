From hashicorp/terraform:0.11.5

RUN apk -v --update add \
        python \
        py-pip \
        && \
    pip install --upgrade awscli && \
    apk -v --purge del && \
    rm /var/cache/apk/*

