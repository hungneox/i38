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

