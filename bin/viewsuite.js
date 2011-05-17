window.testResults = function(r) {
   $(document).ready(function() {
      $.each(r, function(k,v) {
	 var r = $("<tr></tr>")
	    .addClass(v.status)
	    .appendTo($("#restab"));
	 var rv = function(nm) {
	    $("<p></p>")
	       .addClass(nm)
	       .text(v[nm] || "--")
	       .appendTo($("<td></td>").addClass(nm).appendTo(r));
	 };
	 rv("test");
	 rv("suite");
	 rv("pyver");
	 rv("status");
	 rv("exception");
	 rv("stderr");
	 rv("stdout");
      });
   });
};