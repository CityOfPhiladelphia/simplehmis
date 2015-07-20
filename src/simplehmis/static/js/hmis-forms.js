(function($) {
  'use strict';

  $(function() {
    var $selector = $('#id_members-0-hoh_relationship');

    $selector
      .find('option[value="1"]')
      .attr('selected', 'selected');
  });

})(django.jQuery);