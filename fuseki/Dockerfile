FROM stain/jena-fuseki:3.6.0

ADD shiro.ini /jena-fuseki/shiro.ini

CMD ["/jena-fuseki/fuseki-server", "--loc=/fuseki", "--update", "/ds"]
