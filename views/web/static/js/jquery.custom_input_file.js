/*
	By Osvaldas Valutis, www.osvaldas.info
	Available for use under the MIT License
*/

'use strict';

var $input = $form.find('input[type="file"]'),
    $label = $form.find('label'),
    showFiles = function(files) {
		$label.text(files.length > 1 ? ($input.attr('data-multiple-caption') || '').replace( '{count}', files.length ) : files[ 0 ].name);
    };


<<<<<<< HEAD
;( function($, window, document, undefined)
=======
;( function( $, window, document, undefined )
>>>>>>> 804cd7697fa46b4e8d22c3d09f9031a1066f56ea
{
	$( '.inputfile' ).each( function()
	{
		var $input	 = $( this ),
			$label	 = $input.next( 'label' ),
			labelVal = $label.html();

<<<<<<< HEAD
		$input
		.on( 'change', function( e )
=======
		$input.on( 'change', function( e )
>>>>>>> 804cd7697fa46b4e8d22c3d09f9031a1066f56ea
		{
			var fileName = '';

			if( this.files && this.files.length > 1 )
				fileName = ( this.getAttribute( 'data-multiple-caption' ) || '' ).replace( '{count}', this.files.length );
			else if( e.target.value )
				fileName = e.target.value.split( '\\' ).pop();

			if( fileName )
				$label.find( 'span' ).html( fileName );
			else
				$label.html( labelVal );
<<<<<<< HEAD
		})
		.on('click', function () {
			droppedFiles = false;
=======
>>>>>>> 804cd7697fa46b4e8d22c3d09f9031a1066f56ea
		});

		// Firefox bug fix
		$input
		.on( 'focus', function(){ $input.addClass( 'has-focus' ); })
		.on( 'blur', function(){ $input.removeClass( 'has-focus' ); });
	});
<<<<<<< HEAD
})(jQuery, window, document);

$input.on('change', function(e) { // when drag & drop is NOT supported
	droppedFiles = false;
	showFiles(e.target.files);
	//$form.trigger('submit');
=======
})( jQuery, window, document );

$input.on('change', function(e) { // when drag & drop is NOT supported
	//$form.trigger('submit');
	showFiles(e.target.files);
>>>>>>> 804cd7697fa46b4e8d22c3d09f9031a1066f56ea
});