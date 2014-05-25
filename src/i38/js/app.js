function post_comment(e){
   e.preventDefault();
   var data = $('#formComment').serialize();

    $.ajax({
          type: 'POST',
          url: '/api/post_comment',
          data: data,
          dataType: 'json'
      }).done(function(data, textStatus, jqXHR){
        window.location.href = "/news/"+data.page_id;
      }).fail(function(data, textStatus, jqXHR){
          console.log(data.error);
      });
}

$(function() {
    $('#newslist article').each(function(i,news) {
        var news_id = $(news).data("news-id");
        news = $(news);
        up = news.find(".uparrow");
        down = news.find(".downarrow");
        var voted = up.hasClass("voted") || down.hasClass("voted");
        if (!voted) {
            up.click(function(e) {
                if (typeof(apisecret) == 'undefined') return; // Not logged in
                e.preventDefault();
                var data = {
                    page_id: page_id,
                    vote_type: "up",
                    apisecret: apisecret
                };
                $.ajax({
                    type: "POST",
                    url: "/api/votepage",
                    data: data,
                }).done(function(r) {
                    if (r.status == "ok") {
                        n = $("article[data-news-id="+news_id+"]");
                        n.find(".uparrow").addClass("voted");
                        n.find(".downarrow").addClass("disabled");
                    } else {
                        alert(r.error);
                    }
                });
            });
          }

          down.click(function(e) {
                if (typeof(apisecret) == 'undefined') return; // Not logged in
                e.preventDefault();
                var data = {
                    page_id : page_id,
                    vote_type: "down",
                    apisecret: apisecret
                };
                $.ajax({
                    type: "POST",
                    url: "/api/votepage",
                    data: data,
                  }).done(function(r) {
                        if (r.status == "ok") {
                            n = $("article[data-news-id="+news_id+"]");
                            n.find(".uparrow").addClass("disabled");
                            n.find(".downarrow").addClass("voted");
                        } else {
                            alert(r.error);
                        }
                    });
          });
    });
});
