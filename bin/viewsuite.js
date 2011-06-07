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
	 
	 var pupv = function(nm, unesc) {
	    rv = $("<p></p>")
	       .addClass(nm)
	       .text("click")
	       .appendTo($("<td></td>").addClass(nm).appendTo(r));	    
	    if (!v[nm])
	       rv.text("(none)");
	    else
	       rv.click(function() {
		  var t = !!unesc ? unescape(v[nm]) : v[nm];
		  alert(t);
	       });
	 };

	 rv("test");
	 rv("suite");
	 rv("pyver");
	 rv("status");
	 rv("exception");
	 pupv("stderr");
	 pupv("stdout");
	 pupv("last_written", true);
	 pupv("last_read", true);
      });
   });
};