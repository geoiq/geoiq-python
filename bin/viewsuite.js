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
		  var val = v[nm];
		  if ($.isArray(val)) {
		     $.each(val, function(idx,vv) {
			var t = !!unesc ? unescape(vv) : vv;
			alert(t);
		     });
		  } else {
		     var t = !!unesc ? unescape(v[nm]) : v[nm];
		     alert(t);
		  }
	       });
	 };

	 

	 rv("test");
	 rv("suite");
	 rv("pyver");
	 rv("status");
	 pupv("exception");
	 pupv("stderr");
	 pupv("stdout");
	 $("<td>(click)</td>").appendTo(r).click(function() {
	    var writes = v["last_written"];
	    var reads = v["last_read"];
	    console.log("here",writes, reads);
	    var tab = $("<table class='wire'></table>");
	    for (var i =0; i < writes.length; i++) {
	       (function(wr,rd) {
		  var row = $("<tr></tr>").appendTo(tab);
		  var fst_w = wr.split("\n").slice(0,1).join("\n");
		  var fst_r = rd.split("\n").slice(0,1).join("\n");
		  console.log("huh", fst_w, fst_r, $("<td></td>").text(fst_w));
		  row.append(
		     $("<td class='wr'></td>")
			.text(fst_w)
			.click(
			   function() { alert(wr); } 
			) 
		  );
		  row.append(
		     $("<td class='rd'></td>")
			.text(fst_r)
			.click(
			   function() { alert(rd); } 
			) 
		  );
	       })(unescape(writes[i]), unescape(reads[i]));
	    }
	    tab.dialog();
	 });
	 //pupv("last_written", true);
	 //pupv("last_read", true);
      });
   });
};