(function($) {
  'use strict';

  function dismissRelatedLookupPopup(win, chosenId) {
    // Override dismissRelatedLookupPopup from
    // /static/admin/js/admin/RelatedObjectLookup.js
    // to trigger a change on the updated element at
    // the end.
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
      elem.value += ',' + chosenId;
    } else {
      elem.value = chosenId;
    }

    $(elem).trigger('change');
    win.close();
  }
  window.dismissRelatedLookupPopup = dismissRelatedLookupPopup;


  function renderRelated(evt) {
    var $rawFields;

    function extractType(path) {
      var pieces = path.split('/');
      while (pieces[0] === '' || pieces[0] === 'admin') {
        pieces = pieces.slice(1);
      }
      return pieces[0] + '.' + pieces[1];
    }

    // If renderRelated is being called in response to an event, use the event
    // target. Otherwise, render the related str representation for all raw id
    // fields.
    if (evt) {
      $rawFields = $(evt.currentTarget);
    } else {
      $rawFields = $('.vForeignKeyRawIdAdminField');
    }

    $rawFields.each(function(i, rawField) {
      var $rawField = $(rawField),
          $searchButton = $rawField.siblings('.related-lookup'),
          $fieldRep = $rawField.siblings('strong'),
          objectId = $rawField.val();

      if (!objectId) { return; }

      if ($fieldRep.length === 0) {
        $fieldRep = $('<strong/>').insertAfter($searchButton);
      }

      $.get('/get-strrep',
        {
          contenttype: extractType($searchButton.attr('href')),
          id: $rawField.val()
        },
        function(data) {
          $fieldRep.html(data);
        });
    });
  }

  $(function() {
    $('body').on('change', '.vForeignKeyRawIdAdminField', renderRelated);
    renderRelated();
  });

})(django.jQuery);