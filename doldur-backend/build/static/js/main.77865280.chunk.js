(this["webpackJsonpdoldur-frontend"]=this["webpackJsonpdoldur-frontend"]||[]).push([[0],{162:function(e,t,a){e.exports=a(202)},167:function(e,t,a){},175:function(e,t,a){},193:function(e,t,a){},194:function(e,t,a){},195:function(e,t,a){},196:function(e,t,a){},198:function(e,t,a){},199:function(e,t,a){},200:function(e,t,a){},201:function(e,t,a){},202:function(e,t,a){"use strict";a.r(t);var n=a(0),r=a.n(n),s=a(17),o=a.n(s),c=(a(167),a(19)),i=a(20),l=a(21),u=a(22),m=a(56),h=a(143),d=a(275),p=a(98),g=a(146),v=a(145),f=a(103),y=a(264),C=a(75),E=a.n(C),k=a(137),S=a.n(k),b=a(136),F=a.n(b),D=a(135),N=a.n(D),O=a(138),w=a.n(O),A=a(24),j=a(61),x=a(263),T=a(134),M=a.n(T),I=a(72),z=function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).gapi=window.gapi,n.CLIENT_ID="531687826330-d2raf921gt5ur2q5lspcv25ceak6v7e7.apps.googleusercontent.com",n.API_KEY="AIzaSyC1JqJ83f1CZ8Otm-lDrpCX443r7OWewbw",n.DISCOVERY_DOCS=["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"],n.SCOPES="https://www.googleapis.com/auth/calendar.events",n}return Object(i.a)(a,[{key:"convertDay",value:function(e){var t=parseInt(e.slice(8,10))-14,a=parseInt(e.slice(11,13)),n=parseInt(e.slice(14));return"2020-10-"+(12+t)+"T"+(a<10?"0":"")+a+":"+(n<10?"0":"")+n+":00+03:00"}},{key:"convertEvents",value:function(){var e=this,t=Array(0);return void 0===this.props.events?[]:(this.props.events.map((function(a){"course"===a.type&&t.push({summary:a.title,start:{timeZone:"Turkey",dateTime:e.convertDay(a.startDate)},end:{timeZone:"Turkey",dateTime:e.convertDay(a.endDate)},recurrence:["RRULE:FREQ=WEEKLY;COUNT=14"]})})),t)}},{key:"handleExport",value:function(){var e=this,t=this.convertEvents(),a=!1;t.map((function(e){return console.log(e)})),I.a.load("client:auth2",(function(){I.a.client.init({apiKey:e.API_KEY,clientId:e.CLIENT_ID,discoveryDocs:e.DISCOVERY_DOCS,scope:e.SCOPES}),I.a.client.load("calendar","v3",(function(){return console.log("added to calendar!")})),I.a.auth2.getAuthInstance().signIn().then((function(){t.map((function(e){I.a.client.calendar.events.insert({calendarId:"primary",resource:e}).execute((function(e){console.log(e),void 0===e.htmlLink||a||(a=!0,window.open(e.htmlLink))}))}))}))}))}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"export-calendar-wrapper"},r.a.createElement(x.a,{variant:"contained",color:"secondary",startIcon:r.a.createElement(M.a,null),onClick:function(){return e.handleExport()}},"Export to Google"))}}]),a}(r.a.Component),H=(a(175),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"render",value:function(){return r.a.createElement("div",{className:"dayscale-row"},r.a.createElement("div",{className:"dayscale-label"},"Mon"),r.a.createElement("div",{className:"dayscale-label"},"Tue"),r.a.createElement("div",{className:"dayscale-label"},"Wed"),r.a.createElement("div",{className:"dayscale-label"},"Thu"),r.a.createElement("div",{className:"dayscale-label"},"Fri"),r.a.createElement("div",{className:"dayscale-label"},"Sat"),r.a.createElement("div",{className:"dayscale-label"},"Sun"))}}]),a}(r.a.Component)),B=function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).AppointmentContent=function(e){var t=e.data,a=Object(p.a)(e,["data"]);return r.a.createElement(j.a.AppointmentContent,Object.assign({data:t},a,{className:"program-appointment",style:{background:t.color.main}}),"course"===t.type?r.a.createElement("div",{className:"program-text-container"},r.a.createElement("div",{className:"program-title",style:{color:t.color.text}},t.title+"/"+t.section),r.a.createElement("div",{className:"program-title",style:{color:t.color.text}},t.classroom)):r.a.createElement("div",{className:"program-text-container"},r.a.createElement("div",{className:"program-row"},r.a.createElement(g.a,{onClick:function(){return n.props.onDontFillDelete(t.startDate)}},r.a.createElement(E.a,{className:"dont-fill-button",fontSize:"small",color:"secondary"})),r.a.createElement("div",{className:"program-title-dont-fill",style:{color:t.color.text}},t.title))))},n.TimeTableCell=function(e){var t=e.startDate,a=e.endDate,s=(e.onDontFillAdd,Object(p.a)(e,["startDate","endDate","onDontFillAdd"]));return r.a.createElement(j.c.TimeTableCell,Object.assign({},s,{onClick:function(){return n.handleDontFillAdd(t,a)}}))},n.state={currentScenario:0},n}return Object(i.a)(a,[{key:"handleScenarioChange",value:function(e){this.setState({currentScenario:Math.min(this.props.scenarios.length-1,Math.max(0,this.state.currentScenario+e))})}},{key:"handleScenarioChangeAbsolute",value:function(e){var t=isNaN(e)?1:e;this.setState({currentScenario:Math.min(this.props.scenarios.length-1,Math.max(0,t-1))})}},{key:"handleDontFillAdd",value:function(e,t){this.props.onDontFillAdd(e,t)}},{key:"convertTime",value:function(e,t,a){return"2021-02-"+(14+e)+"T"+(t<10?"0":"")+t+":"+(a<10?"0":"")+a}},{key:"convertToEntry",value:function(){var e=this,t=Array(0);return(this.props.scenarios.length>0?this.props.scenarios[this.state.currentScenario]:[]).map((function(a){a.section.lectureTimes.map((function(n){for(var r=n.startHour;r<n.endHour;r++)t.push({type:"course",title:a.abbreviation,section:a.section.sectionNumber,classroom:void 0!==n.classroom?n.classroom:"-",startDate:e.convertTime(n.day,r,n.startMin),endDate:e.convertTime(n.day,r+1,n.endMin),color:a.color})}))})),this.props.dontFills.map((function(e){t.push({type:"dontFill",title:"FULL",color:{main:"#000000",text:"#FFFFFF"},startDate:e.startDate,endDate:e.endDate})})),t}},{key:"CustomAppointment",value:function(e){e.formatDate;var t=Object(p.a)(e,["formatDate"]);return r.a.createElement(j.c.AppointmentLayer,Object.assign({},t,{formatDate:function(e){return""},className:"custom-appointment"}))}},{key:"render",value:function(){var e=this,t=this.convertToEntry();return r.a.createElement("div",{className:m.isMobile?"scheduler-mobile":"scheduler-wrapper"},r.a.createElement(v.a,null,r.a.createElement(j.b,{id:"scheduler",data:t},r.a.createElement(A.q,{currentDate:"2021-02-20"}),r.a.createElement(j.c,{startDayHour:7.667,endDayHour:17.5,cellDuration:60,dayScaleRowComponent:H,appointmentLayerComponent:this.CustomAppointment,timeTableCellComponent:this.TimeTableCell}),r.a.createElement(j.a,{appointmentContentComponent:this.AppointmentContent}))),r.a.createElement("div",{className:"program-vertical"},this.props.scenarios.length>0?r.a.createElement("div",{className:"program-row"},r.a.createElement(g.a,{onClick:function(){return e.handleScenarioChange(-10)}},r.a.createElement(N.a,{fontSize:"small"})),r.a.createElement(g.a,{onClick:function(){return e.handleScenarioChange(-1)}},r.a.createElement(F.a,{fontSize:"small"})),r.a.createElement("div",{className:"program-typo-wrapper"},r.a.createElement(f.a,null,"Scenario ")),r.a.createElement("div",{className:"program-textfield-wrapper"},r.a.createElement(y.a,{className:"program-textfield",type:"number",value:this.state.currentScenario+1,onChange:function(t){return e.handleScenarioChangeAbsolute(parseInt(t.target.value))}})),r.a.createElement("div",{className:"program-typo-wrapper"},r.a.createElement(f.a,null," of "+this.props.scenarios.length)),r.a.createElement(g.a,{onClick:function(){return e.handleScenarioChange(1)}},r.a.createElement(S.a,{fontSize:"small"})),r.a.createElement(g.a,{onClick:function(){return e.handleScenarioChange(10)}},r.a.createElement(w.a,{fontSize:"small"}))):null,this.props.scenarios.length>0&&!m.isMobile?r.a.createElement("div",{className:"program-calendar-wrapper"},r.a.createElement(z,{events:t})):null))}}]),a}(r.a.Component),L=a(282),Y=a(281),P=a(207),U=a(212),R=a(210),W=a(208),K=a(271),Z=a(277),_=a(141),q=a.n(_),J=a(142),G=a.n(J),V=a(34),Q=a.n(V),X=a(50),$=a(102),ee=a.n($),te=function(){function e(){Object(c.a)(this,e),this.coursesUrl="https:\\robotdegilim.xyz/courses",this.mustUrl="https:\\robotdegilim.xyz/musts?"}return Object(i.a)(e,[{key:"getMusts",value:function(){var e=Object(X.a)(Q.a.mark((function e(t,a){var n;return Q.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return n=this.mustUrl+"dept="+t+"&sem="+a,e.next=3,ee.a.get(n);case 3:return e.abrupt("return",e.sent.data);case 4:case"end":return e.stop()}}),e,this)})));return function(t,a){return e.apply(this,arguments)}}()},{key:"getCourses",value:function(){var e=Object(X.a)(Q.a.mark((function e(){var t,a;return Q.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,ee.a.get(this.coursesUrl);case 2:return t=e.sent.data,a=Array(0),Object.keys(t).map((function(e){var n={code:e,abbreviation:t[e]["Course Name"].slice(0,t[e]["Course Name"].search(" ")),name:t[e]["Course Name"].slice(t[e]["Course Name"].search("-")+2),category:0,sections:Array(0)};Object.keys(t[e].Sections).map((function(a){var r=t[e].Sections[a],s={instructor:r.i[0],sectionNumber:a,criteria:Array(0),minYear:0,maxYear:0,lectureTimes:Array(0)};r.t.map((function(e){s.lectureTimes.push({classroom:e.p,day:e.d,startHour:parseInt(e.s.slice(0,e.s.search(":"))),startMin:parseInt(e.s.slice(e.s.search(":")+1)),endHour:parseInt(e.e.slice(0,e.e.search(":"))),endMin:parseInt(e.e.slice(e.e.search(":")+1))})})),r.c.map((function(e){s.criteria.push({dept:e.d,surnameStart:e.s,surnameEnd:e.e})})),n.sections.push(s)})),a.push(n)})),e.abrupt("return",a);case 6:case"end":return e.stop()}}),e,this)})));return function(){return e.apply(this,arguments)}}()}]),e}();function ae(){return ne.apply(this,arguments)}function ne(){return(ne=Object(X.a)(Q.a.mark((function e(){var t;return Q.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=new te,e.next=3,t.getCourses();case 3:return e.abrupt("return",e.sent);case 4:case"end":return e.stop()}}),e)})))).apply(this,arguments)}function re(){return(re=Object(X.a)(Q.a.mark((function e(t,a){var n;return Q.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return n=new te,e.abrupt("return",n.getMusts(t,a));case 2:case"end":return e.stop()}}),e)})))).apply(this,arguments)}function se(e,t,a){var n={A:1,B:2,C:3,"\xc7":4,D:5,E:6,F:7,G:8,"\u011e":9,H:10,I:11,"\u0130":12,J:13,K:14,L:15,M:16,N:17,O:18,"\xd6":19,P:20,Q:21,R:22,S:23,"\u015e":24,T:25,U:26,"\xdc":27,V:28,W:29,X:30,Y:31,Z:32},r=n[e[0]],s=n[e[1]],o=n[t[0]],c=n[t[1]],i=n[a[0]],l=n[a[1]];return o<r&&r<i||(o===r&&r<i&&c<=c||o<r&&r===i&&s<=l)}function oe(e,t,a,n){for(var r=n.sections.length-1;r>=0;r--){var s=!1;if(!0===n.sections[r].toggle)for(var o=0;o<n.sections[r].criteria.length;o++){var c=n.sections[r].criteria[o],i=!1,l=!1;!1===n.checkDepartment?i=!0:"ALL"!==c.dept&&c.dept!==t||(i=!0),(!1===n.checkSurname||!0===se(e,c.surnameStart,c.surnameEnd))&&(l=!0),!0===i&&!0===l&&(s=!0)}!1===s&&n.sections.splice(r,1)}return n}function ce(e,t){return!(e.day!==t.day||e.startHour>t.endHour||t.startHour>e.endHour||e.startHour===t.endHour&&e.startMin>t.endMin||t.startHour===e.endHour&&t.startMin>e.endMin)}function ie(e,t){for(var a=e.lectureTimes,n=t.lectureTimes,r=0;r<a.length;r++)for(var s=0;s<n.length;s++)if(!0===ce(a[r],n[s]))return!0;return!1}function le(e,t){for(var a=e.lectureTimes,n=t.times,r=0;r<a.length;r++)for(var s=0;s<n.length;s++)if(!0===ce(a[r],n[s]))return!0;return!1}function ue(e,t,a,n,r){var s=n.length,o=[];return function e(t,a,n,r,s,o){if(n===t.length){var c=Array(0);return r.map((function(e){c.push({code:e.code,section:e.section.sectionNumber})})),void(c.length==o&&s.push(c))}for(var i=0;i<t[n].sections.length;i++){for(var l=!1,u=0;u<r.length;u++)1==t[n].checkCollision&&1==r[u].collision&&!0===ie(t[n].sections[i],r[u].section)&&(l=!0);for(u=0;u<a.length;u++)!0===le(t[n].sections[i],a[u])&&(l=!0);!1===l&&(r.push({code:t[n].code,section:t[n].sections[i],collision:t[n].checkCollision}),e(t,a,n+1,r,s,o),r.pop())}}(n=function(e,t,a,n){for(var r=n.length-1;r>=0;r--)n[r]=oe(e,t,a,n[r]),0===n[r].sections.length&&n.splice(r,1);return n}(e,t,a,n),r,0,[],o,s),o}var me=a(268),he=a(279),de=a(269),pe=a(280),ge=a(272),ve=a(273),fe=a(76),ye=a.n(fe),Ce=a(68),Ee=a.n(Ce),ke=(a(193),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],n}return Object(i.a)(a,[{key:"formatTime",value:function(e){return e>9?e.toString():"0"+e.toString()}},{key:"getDepartmentCriteria",value:function(){for(var e="",t=0;t<this.props.sectionDetails.dept.length;t++)e+=this.props.sectionDetails.dept[t]+" ";return e}},{key:"renderTimes",value:function(){var e=this,t=Array(0);return this.props.sectionDetails.lectureTimes.map((function(a){t.push(r.a.createElement("div",{className:"section-date",style:{background:e.props.color.ternary}},r.a.createElement("div",{className:"time-row"},e.days[a.day]+" "+a.startHour+"."+e.formatTime(a.startMin)+"-"+a.endHour+"."+e.formatTime(a.endMin)),r.a.createElement("div",{className:"time-row"},"Classroom: "+a.classroom)))})),t}},{key:"renderCriteria",value:function(e){return r.a.createElement("div",{className:"section-row"},"Department: "+e.dept+" Surname: "+e.surnameStart+"-"+e.surnameEnd)}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"section-info",style:{background:this.props.color.secondary}},r.a.createElement("div",null,"Section "+this.props.sectionDetails.sectionNumber),r.a.createElement(K.a,null),r.a.createElement("div",{className:"section-row"},"Instructor: "+this.props.sectionDetails.instructor),this.props.sectionDetails.criteria.map((function(t){return e.renderCriteria(t)})),r.a.createElement("div",{className:"section-row"},this.renderTimes()))}}]),a}(r.a.Component)),Se=a(89),be=a.n(Se),Fe=(a(194),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"handleSurnameCheck",value:function(){this.props.onSettingsChange({checkSurname:!this.props.settings.checkSurname,checkDepartment:this.props.settings.checkDepartment,checkCollision:this.props.settings.checkCollision})}},{key:"handleDepartmentCheck",value:function(){this.props.onSettingsChange({checkSurname:this.props.settings.checkSurname,checkDepartment:!this.props.settings.checkDepartment,checkCollision:this.props.settings.checkCollision})}},{key:"handleCollisionCheck",value:function(){this.props.onSettingsChange({checkSurname:this.props.settings.checkSurname,checkDepartment:this.props.settings.checkDepartment,checkCollision:!this.props.settings.checkCollision})}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"course-settings-wrapper"},r.a.createElement(pe.a,{style:{background:this.props.color.secondary}},r.a.createElement(ge.a,{expandIcon:r.a.createElement(Ee.a,null),"aria-controls":"panel1a-content"},r.a.createElement("div",{className:"course-settings-row"},r.a.createElement(be.a,{color:"primary",fontSize:"large"}),r.a.createElement("div",{className:"settings-typo"},r.a.createElement(f.a,null,"Advanced Settings")))),r.a.createElement(ve.a,null,r.a.createElement("div",{className:"settings-accordion"},r.a.createElement(K.a,null),r.a.createElement("div",{className:"settings-row"},r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:this.props.settings.checkSurname,onChange:function(){return e.handleSurnameCheck()},color:"primary"}),label:"Check surname"}),r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:this.props.settings.checkDepartment,onChange:function(){return e.handleDepartmentCheck()},color:"primary"}),label:"Check department"}),r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:this.props.settings.checkCollision,onChange:function(){return e.handleCollisionCheck()},color:"primary"}),label:"Check collision"}))))))}}]),a}(r.a.Component)),De=(a(195),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).state={selectedSections:Array(e.course.sections.length).fill(!0),sectionCount:e.course.sections.length},n}return Object(i.a)(a,[{key:"handleToggle",value:function(e){this.props.onToggle(e)}},{key:"handleSettingsChange",value:function(e){this.props.onSettingsChange(e)}},{key:"toggleSections",value:function(){var e=Array(this.state.sectionCount).fill(!this.state.selectedSections[0]);this.setState({selectedSections:e}),this.handleToggle(e)}},{key:"renderCheckBoxes",value:function(){var e=this;if(this.state.sectionCount<=0)return null;for(var t=Array(0),a=function(a){t.push(r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:e.state.selectedSections[a],onChange:function(t){var n=e.state.selectedSections.slice(0);n[a]=!n[a],e.setState({selectedSections:n}),e.handleToggle(n)},color:"primary"}),label:e.props.course.sections[a].sectionNumber}))},n=0;n<this.state.sectionCount;n++)a(n);return r.a.createElement(de.a,{row:!0},t,r.a.createElement(x.a,{color:"primary",onClick:function(){return e.toggleSections()}},"Toggle"))}},{key:"renderSectionDetails",value:function(){for(var e=Array(0),t=0;t<this.props.course.sections.length;t++)e.push(r.a.createElement(ke,{sectionNo:t+1,sectionDetails:this.props.course.sections[t],color:this.props.color}));return e}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"course-card",style:{background:this.props.color.main}},r.a.createElement("div",{className:"course-row"},r.a.createElement(g.a,{size:"small",onClick:function(){return e.props.onDelete()}},r.a.createElement(ye.a,{fontSize:"inherit"})),r.a.createElement(pe.a,{className:"course-accordion",style:{background:this.props.color.main}},r.a.createElement(ge.a,{expandIcon:r.a.createElement(Ee.a,null),"aria-controls":"panel1a-content"},r.a.createElement(f.a,{style:{color:this.props.color.text}},this.props.course.abbreviation+": "+this.props.course.name)),r.a.createElement(ve.a,null,r.a.createElement("div",{className:"course-details"},r.a.createElement("div",{className:"course-left-row"},r.a.createElement(f.a,{style:{color:this.props.color.text}},"Course code: "+this.props.course.code)),r.a.createElement(K.a,null),r.a.createElement("div",{className:"course-centered-row"},r.a.createElement("div",null,"Sections")),r.a.createElement(K.a,null),r.a.createElement("div",{className:"course-row"},this.renderCheckBoxes()),r.a.createElement("div",null,r.a.createElement(Fe,{color:this.props.color,onSettingsChange:function(t){return e.handleSettingsChange(t)},settings:this.props.settings})),r.a.createElement(K.a,null),this.renderSectionDetails())))))}}]),a}(r.a.Component)),Ne=a(278),Oe=a(140),we=a.n(Oe),Ae=(a(196),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).state={course:null,category:-1},n}return Object(i.a)(a,[{key:"handleCourseAdd",value:function(){this.props.onCourseAdd(this.state.course),this.setState({course:null,category:-1})}},{key:"render",value:function(){var e,t,a=this;return r.a.createElement("div",{className:"add-course-wrapper"},r.a.createElement("div",{className:"add-course-row"},r.a.createElement(P.a,{className:"category-form",variant:"outlined"},r.a.createElement(R.a,{className:"category-select",value:this.state.category,onChange:function(e){return a.setState({category:e.target.value,course:null})},inputProps:{id:"category-select"}},r.a.createElement(L.a,{value:-1},"All courses"),r.a.createElement(L.a,{value:0},"Must"),r.a.createElement(L.a,{value:1},"Technical"),r.a.createElement(L.a,{value:2},"Restricted"),r.a.createElement(L.a,{value:3},"Non-Tech"))),r.a.createElement(Ne.a,{className:"add-course-name",options:(e=this.props.courses,t=this.state.category,t<0?e:e.filter((function(e){return e.category===t}))),getOptionLabel:function(e){return e.abbreviation+": "+e.name},style:{width:"60%"},value:this.state.course,renderInput:function(e){return r.a.createElement(y.a,Object.assign({},e,{label:"Course name",variant:"outlined"}))},onChange:function(e,t){return a.setState({course:t})}}),null!==this.state.course?r.a.createElement(g.a,{onClick:function(){return a.handleCourseAdd()}},r.a.createElement(we.a,{fontSize:"large",color:"primary"})):null))}}]),a}(r.a.Component)),je=(a(198),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"render",value:function(){return r.a.createElement("div",{className:"df-widget-wrapper"},"Custom Don't Fills are coming soon *-*")}}]),a}(r.a.Component)),xe=(a(199),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(){return Object(c.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"handleSurnameCheck",value:function(){this.props.onSettingsChange({checkSurname:!this.props.settings.checkSurname,checkDepartment:this.props.settings.checkDepartment,checkCollision:this.props.settings.checkCollision})}},{key:"handleDepartmentCheck",value:function(){this.props.onSettingsChange({checkSurname:this.props.settings.checkSurname,checkDepartment:!this.props.settings.checkDepartment,checkCollision:this.props.settings.checkCollision})}},{key:"handleCollisionCheck",value:function(){this.props.onSettingsChange({checkSurname:this.props.settings.checkSurname,checkDepartment:this.props.settings.checkDepartment,checkCollision:!this.props.settings.checkCollision})}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"course-settings-wrapper"},r.a.createElement(pe.a,{style:{background:"aliceblue"}},r.a.createElement(ge.a,{expandIcon:r.a.createElement(Ee.a,null),"aria-controls":"panel1a-content"},r.a.createElement("div",{className:"course-settings-row"},r.a.createElement(be.a,{color:"primary",fontSize:"large"}),r.a.createElement("div",{className:"course-settings-typo"},r.a.createElement(f.a,null,"Advanced Settings")))),r.a.createElement(ve.a,null,r.a.createElement("div",{className:"course-settings-accordion"},r.a.createElement(K.a,null),r.a.createElement("div",{className:"course-settings-row"},r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:this.props.settings.checkSurname,onChange:function(){return e.handleSurnameCheck()},color:"primary"}),label:"Check surname"}),r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:this.props.settings.checkDepartment,onChange:function(){return e.handleDepartmentCheck()},color:"primary"}),label:"Check department"}),r.a.createElement(me.a,{control:r.a.createElement(he.a,{checked:this.props.settings.checkCollision,onChange:function(){return e.handleCollisionCheck()},color:"primary"}),label:"Check collision"}))))))}}]),a}(r.a.Component)),Te=function(){function e(){Object(c.a)(this,e),this.colors=[{main:"#33CDE8",secondary:"#FFFFFF",ternary:"#C3F6FF",text:"#000000",textSection:"#FFFFFF"},{main:"#FF38CB",secondary:"#FFFFFF",ternary:"#F7DCFF",text:"#000000",textSection:"#FFFFFF"},{main:"#FFF040",secondary:"#FFFFFF",ternary:"#F7F3C2",text:"#000000",textSection:"#FFFFFF"},{main:"#71F154",secondary:"#FFFFFF",ternary:"#DDF7D7",text:"#000000",textSection:"#FFFFFF"},{main:"#E82A2A",secondary:"#FFFFFF",ternary:"#FFA9A9",text:"#000000",textSection:"#FFFFFF"},{main:"#FF8F00",secondary:"#FFFFFF",ternary:"#FFD39A",text:"#000000",textSection:"#FFFFFF"},{main:"#B59FF7",secondary:"#FFFFFF",ternary:"#E9E2FE",text:"#000000",textSection:"#FFFFFF"},{main:"#8D969A",secondary:"#FFFFFF",ternary:"#CAD2D5",text:"#000000",textSection:"#FFFFFF"}],this.iterator=-1}return Object(i.a)(e,[{key:"getNextColor",value:function(){return this.colors.length<=0?{main:0,secondary:0,ternary:0}:(this.iterator=(this.iterator+1)%this.colors.length,this.colors[this.iterator])}}]),e}(),Me=(a(200),function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).state={surname:"",department:"",semester:0,alertMsg:"",errorDept:!1,errorSemester:!1,errorSurname:!1,selectedCourses:[],allCourses:[],settings:{checkSurname:!0,checkDepartment:!0,checkCollision:!0},scenarios:[],colorset:new Te},n}return Object(i.a)(a,[{key:"componentDidMount",value:function(){var e=this;document.title="Robot De\u011filim *-*",ae().then((function(t){return e.setState({allCourses:t})})),m.isMobile&&(document.body.style.zoom="60%")}},{key:"getCourseByCode",value:function(e){for(var t=0;t<this.state.allCourses.length;t++)if(this.state.allCourses[t].code===e)return this.state.allCourses[t];return null}},{key:"getSectionByNumber",value:function(e,t){for(var a=0;a<e.sections.length;a++)if(e.sections[a].sectionNumber===t)return e.sections[a];return null}},{key:"getColorByCourseCode",value:function(e){for(var t=0;t<this.state.selectedCourses.length;t++)if(null!==this.state.selectedCourses[t]&&this.state.selectedCourses[t].code===e)return this.state.selectedCourses[t].color;return null}},{key:"renderSemesterSelections",value:function(e){var t=Array(0);t.push(r.a.createElement(L.a,{value:0},"---"));for(var a=0;a<e;a++)t.push(r.a.createElement(L.a,{value:a+1},a+1));return t}},{key:"handleAddMustCourse",value:function(){var e=this;this.setState({alertMsg:"",errorDept:!1,errorSemester:!1,errorSurname:!1}),this.state.department.length<2?this.setState({alertMsg:"Please enter a correct department",errorDept:!0}):this.state.semester<1?this.setState({alertMsg:"Please choose a semester",errorSemester:!0}):function(e,t){return re.apply(this,arguments)}(this.state.department,this.state.semester).then((function(t){void 0!==t&&t.map((function(t){var a=!1;e.state.selectedCourses.map((function(e){null!==e&&e.code===t&&(a=!0)})),a||e.handleAddCourse(e.getCourseByCode(t))}))})).catch((function(t){e.setState({alertMsg:"Must courses for your department are not available",errorDept:!0})}))}},{key:"handleAlertClose",value:function(){this.setState({alertMsg:""})}},{key:"handleDeleteCourse",value:function(e){var t=this.state.selectedCourses.slice(0);t[e]=null,this.setState({selectedCourses:t})}},{key:"handleToggle",value:function(e,t){var a=this.state.selectedCourses.slice(0);a[e].sections=t,this.setState({selectedCourses:a}),console.log("Course "+e+" sections:"+t)}},{key:"handleAddCourse",value:function(e){if(null!==e){var t=this.state.selectedCourses.slice(0);t.push({code:e.code,sections:Array(e.sections.length).fill(!0),color:this.state.colorset.getNextColor(),settings:{checkSurname:!0,checkDepartment:!0,checkCollision:!0}}),this.setState({selectedCourses:t})}}},{key:"handleCourseSettings",value:function(e,t){var a=this.state.selectedCourses.slice(0);a[e].settings=t,this.setState({selectedCourses:a})}},{key:"handleChangeSettings",value:function(e){this.setState({settings:e})}},{key:"handleScheduleComplete",value:function(e){var t=this;e.length<=0&&(console.log("Fail!"),this.setState({alertMsg:"There is no available schedule for this criteria."}));var a=Array(0);e.map((function(e){var n=Array(0);e.map((function(e){var a=t.getCourseByCode(e.code),r=t.getSectionByNumber(a,e.section),s=t.getColorByCourseCode(e.code);n.push({abbreviation:a.abbreviation,section:r,color:s})})),a.push(n)})),this.props.onSchedule(a)}},{key:"formatDf",value:function(e){return{day:e.startDate.getDay(),startHour:e.startDate.getHours(),startMin:e.startDate.getMinutes(),endHour:e.endDate.getHours(),endMin:e.endDate.getMinutes()-1}}},{key:"handleScheduleBegin",value:function(){var e=this;if(this.setState({alertMsg:"",errorDept:!1,errorSemester:!1,errorSurname:!1}),this.state.department.length<2)this.setState({alertMsg:"Please enter a correct department",errorDept:!0});else if(this.state.surname.length<2&&this.state.settings.checkSurname)this.setState({alertMsg:"Please enter at least 2 letters of your surname",errorSurname:!0});else{var t=Array(0),a=Array(0);this.state.selectedCourses.map((function(a){if(null===a)return null;for(var n=e.getCourseByCode(a.code),r={code:a.code,category:n.category,checkSurname:e.state.settings.checkSurname&&a.settings.checkSurname,checkCollision:e.state.settings.checkCollision&&a.settings.checkCollision,checkDepartment:e.state.settings.checkDepartment&&a.settings.checkDepartment,sections:Array(0)},s=function(e){var t={sectionNumber:n.sections[e].sectionNumber,minYear:n.sections[e].minYear,maxYear:n.sections[e].maxYear,toggle:a.sections[e],criteria:n.sections[e].criteria,lectureTimes:Array(0)};n.sections[e].lectureTimes.map((function(e){return t.lectureTimes.push(e)})),t.criteria.length<=0&&(t.criteria=[{dept:"ALL",surnameStart:"AA",surnameEnd:"ZZ"}]),r.sections.push(t)},o=0;o<n.sections.length;o++)s(o);t.push(r)})),this.props.dontFills.map((function(t){var n=e.formatDf(t);a.push({times:[n]})})),console.log(a);var n=ue(this.state.surname.slice(0,2),this.state.department,0,t,a);this.setState({scenario:n}),this.handleScheduleComplete(n)}}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:m.isMobile?"control-mobile":"control-wrapper"},r.a.createElement(Y.a,{open:""!==this.state.alertMsg,autoHideDuration:5e3,onClose:function(){return e.handleAlertClose()}},r.a.createElement(Z.a,{elevation:6,variant:"filled",onClose:function(){return e.handleAlertClose()},severity:"error"},this.state.alertMsg)),r.a.createElement("div",{className:"control-row"},r.a.createElement("div",{className:"textfield-wrapper"},r.a.createElement(y.a,{required:this.state.settings.checkSurname,error:this.state.errorSurname,label:"Surname",value:this.state.surname,inputProps:{maxLength:12},variant:"outlined",onChange:function(t){return e.setState({surname:t.target.value.toUpperCase()})}})),r.a.createElement("div",{className:"textfield-wrapper"},r.a.createElement(y.a,{required:!0,error:this.state.errorDept,label:"Department",value:this.state.department,inputProps:{maxLength:12},variant:"outlined",onChange:function(t){return e.setState({department:t.target.value.toUpperCase()})}}))),r.a.createElement("div",{className:"control-row"},r.a.createElement("div",{className:"textfield-wrapper"},r.a.createElement(P.a,{className:"form-control"},r.a.createElement(U.a,null,"Semester"),r.a.createElement(R.a,{error:this.state.errorSemester,value:this.state.semester,onChange:function(t){return e.setState({semester:t.target.value})}},this.renderSemesterSelections(8)),r.a.createElement(W.a,null,"Ex: 2nd year Fall semester -> 3"))),r.a.createElement("div",{className:"control-button"},r.a.createElement(x.a,{variant:"contained",color:"secondary",startIcon:r.a.createElement(q.a,null),onClick:function(){return e.handleAddMustCourse()}},"Add Must Courses")),r.a.createElement("div",{className:"control-button"},r.a.createElement(x.a,{variant:"contained",color:"primary",startIcon:r.a.createElement(G.a,null),onClick:function(){return e.handleScheduleBegin()}},"Schedule"))),r.a.createElement(xe,{settings:this.state.settings,onSettingsChange:function(t){return e.handleChangeSettings(t)}}),r.a.createElement(K.a,null),r.a.createElement("div",{className:"control-row"},r.a.createElement("div",{className:"centered-row"},"Added Courses")),r.a.createElement(K.a,null),this.state.selectedCourses.map((function(t,a){return null!==t?r.a.createElement(De,{course:e.getCourseByCode(t.code),onDelete:function(){return e.handleDeleteCourse(a)},onToggle:function(t){return e.handleToggle(a,t)},color:t.color,settings:t.settings,onSettingsChange:function(t){return e.handleCourseSettings(a,t)}}):null})),r.a.createElement(Ae,{courses:this.state.allCourses,onCourseAdd:function(t){return e.handleAddCourse(t)}}),r.a.createElement(je,null))}}]),a}(r.a.Component)),Ie=a(265),ze=a(270),He=a(266),Be=a(274),Le=a(267),Ye=function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).state={open:!0},n}return Object(i.a)(a,[{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"dialog-wrapper"},r.a.createElement(Ie.a,{open:this.state.open,onClose:function(){return e.setState({open:!1})},"aria-labelledby":"alert-dialog-title","aria-describedby":"alert-dialog-description"},r.a.createElement(ze.a,{id:"alert-dialog-title"},"Welcome!"),r.a.createElement(He.a,null,r.a.createElement(Be.a,{id:"alert-dialog-description"},"Siteyi ders se\xe7imine yeti\u015ftirmek i\xe7in h\u0131zl\u0131 bir \u015fekilde yazd\u0131\u011f\u0131m\u0131zdan, her t\xfcrl\xfc hata bildirimi bizim i\xe7in \xe7ok faydal\u0131 olacakt\u0131r. Fark etti\u011finiz herhangi bir s\u0131k\u0131nt\u0131da l\xfctfen bizle ileti\u015fime ge\xe7in.",r.a.createElement("br",null),r.a.createElement("br",null),"Eren Eri\u015fken: erenerisken@gmail.com",r.a.createElement("br",null),"Alperen Kele\u015f: alpkeles99@gmail.com",r.a.createElement("br",null),"Alp Eren Y\u0131lmaz: ylmz.alp.e@gmail.com",r.a.createElement("br",null),r.a.createElement("br",null),"\xd6nemli: Yeni \xf6zellik olarak eklenen Google Calendar export'u kullanmak i\xe7in geli\u015fmi\u015f k\u0131sm\u0131ndan izin vermeniz gerekmektedir.",r.a.createElement("br",null),r.a.createElement("br",null),"doldur.xyz an\u0131s\u0131na! (Sayg\u0131lar @baskinburak)")),r.a.createElement(Le.a,null,r.a.createElement(x.a,{onClick:function(){return e.setState({open:!1})},color:"secondary",variant:"contained",autoFocus:!1},"Close"))))}}]),a}(r.a.Component),Pe=(a(201),Object(h.a)({palette:{secondary:{main:"#71F154"}}})),Ue=function(e){Object(u.a)(a,e);var t=Object(l.a)(a);function a(e){var n;return Object(c.a)(this,a),(n=t.call(this,e)).state={scenarios:[],dontFills:[]},n}return Object(i.a)(a,[{key:"handleDontFillAdd",value:function(e,t){var a=this.state.dontFills.slice(0);a.push({startDate:e,endDate:t}),this.setState({dontFills:a})}},{key:"handleDontFillDelete",value:function(e){this.setState({dontFills:this.state.dontFills.filter((function(t){return t.startDate!==e}))})}},{key:"render",value:function(){var e=this;return r.a.createElement(d.a,{theme:Pe},r.a.createElement("div",{className:"App"},r.a.createElement(Ye,null),r.a.createElement("div",{className:m.isMobile?"column":"row"},r.a.createElement(B,{dontFills:this.state.dontFills,scenarios:this.state.scenarios,onDontFillAdd:function(t,a){return e.handleDontFillAdd(t,a)},onDontFillDelete:function(t){return e.handleDontFillDelete(t)}}),r.a.createElement(Me,{onSchedule:function(t){return e.setState({scenarios:t})},dontFills:this.state.dontFills}))))}}]),a}(r.a.Component);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));o.a.render(r.a.createElement(r.a.StrictMode,null,r.a.createElement(Ue,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[162,1,2]]]);
//# sourceMappingURL=main.77865280.chunk.js.map