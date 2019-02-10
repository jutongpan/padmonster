function populateDataViewer(el){

	$.ajax({
		data: JSON.stringify({
			ID : $(el).find('input[type="hidden"]').val()
		}),
		contentType: 'application/json;charset=UTF-8',
		type: 'POST',
		url: '/monData',
	})
	.done(function(output) {

		if (output.error) {
			$('#monDataViewer').text(output.error);
		}
		else {
			$('#monDataViewer').html(output);
		};

	});

}


$(document).ready(function() {

    $('button[name=AwokenSkillSelector]').click(function() {
      var ASID = $(this).val();
      $('div#selected_awokenskills').append(
        '<button type="button" class="btn btn-default" value="' + ASID + '" style="padding: 0px; margin-right: 1px;">' +
          "<img src='{{ img_source }}img/AwokenSkill/" + ASID + ".png' width='25'>" +
        '</button>'
      );
    });

    $('div#selected_awokenskills').on('click', 'button', function() {
      $(this).remove();
    });

    $('button#ClearAwokenSkill').click(function() {
      $('div#selected_awokenskills').empty();
    });

    $('select#IncSuper').selectpicker('setStyle', 'btn-default btn-sm');


    $('#EnableRange').change(function() {
      if (this.checked) {
        $('#ToId').prop('disabled', false);
        $('#FromId').attr('placeholder', 'From');
        $('#ToId').attr('placeholder', 'To');
      } else {
        $('#ToId').prop('disabled', true);
        $('#FromId').attr('placeholder', 'ID');
        $('#ToId').attr('placeholder', '');
      };
    });


	$('#filter').on('submit', function(event) {

		var selectedAwokenSkillIds = $('div#selected_awokenskills > button').map(function() {
			return $(this).val();
		}).get();

		var selectedTypes = $('div#Type').find('input[type=checkbox]:checked').map(function() {
			return $(this).val();
		}).get();

		var selectedActiveSkillTypes = $('div#ActiveSkill').find('input[type=checkbox]:checked').map(function() {
			return $(this).val();
		}).get();

		$.ajax({
			data: JSON.stringify({
				MainAtt    : $('input[name=selectMainAtt]:checked').val(),
				SubAtt     : $('input[name=selectSubAtt]:checked').val(),
				Type       : selectedTypes,
				Awoken     : selectedAwokenSkillIds,
				IncSuper   : $('#IncSuper').val(),
				Active     : selectedActiveSkillTypes,
				SortBy     : $('select#SortBy').val(),
				TopN       : $('select#TopN').val()
			}),
			contentType: 'application/json;charset=UTF-8',
			type: 'POST',
			url: '/monSearch1',
		})
		.done(function(output) {

			if (output.error) {
				$('#results').text(output.error);
			}
			else {
				$('#results').html(output.Monster);
				populateDataViewer($('#results > button')[0]);
			};

			$('#results')[0].scrollIntoView();

		});

		event.preventDefault();

	});


	$('#FormId').on('submit', function(event) {

		$.ajax({
			data: JSON.stringify({
				FromId    : $('#FromId').val(),
				ToId      : $('#ToId').val()
			}),
			contentType: 'application/json;charset=UTF-8',
			type: 'POST',
			url: '/monSearch2',
		})
		.done(function(output) {

			if (output.error) {
				$('#results').text(output.error);
			}
			else {
				$('#results').html(output.Monster);
				populateDataViewer($('#results > button')[0]);
			};

			$('#results')[0].scrollIntoView();

		});

		event.preventDefault();

	});


	$('#results').on('click', 'button', function(event) {
		
		populateDataViewer($(this));

		$('#monDataViewer')[0].scrollIntoView();

		event.preventDefault();

	});

});