$(document).ready(function(){
    $.ajax({
        url: '/tags',
        method: 'GET'
    })
        .done(function(response){
            zingchart.MODULESDIR='https://cdn.zingchart.com/modules/';
            var myConfig = {
              type: 'wordcloud',
                maxFontSize: '18px',
                backgroundColor: 'transparent',
                  options: {
                        text: response.tags,

                    palette: ['#E91E63','#2196F3','#4CAF50','#FFC107','#00BCD4', '#893bda','#8BC34A' ],
                      style: {
                        padding: '3px',
                        alpha: 0.9,
                        fontFamily: 'Roboto',
                        hoverState: {
                          alpha: 0.3,
                          borderRadius: 3,
                            fontColor: 'whitesmoke',
                          textAlpha: 1,
                        }
	  }
              },
            };
            zingchart.render({
                id: 'myChart',
                data: myConfig,
                height: 300,
                width: '100%',
            });
            zingchart.label_click = function(label){
                window.location.href= `/blogs/search/${label.text}`;
            }
        })
});