(this["webpackJsonpdoldur-frontend"]=this["webpackJsonpdoldur-frontend"]||[]).push([[0],{138:function(e,t,a){e.exports=a(158)},143:function(e,t,a){},150:function(e,t,a){},151:function(e,t,a){},152:function(e,t,a){},153:function(e,t,a){},155:function(e,t,a){},156:function(e,t,a){},157:function(e,t,a){},158:function(e,t,a){"use strict";a.r(t);var n=a(0),r=a.n(n),s=a(17),o=a.n(s),c=(a(143),a(53)),l=a(122),i=a(228),u=a(28),m=a(29),d=a(34),h=a(35),p=a(161),v=a(20),E=a(90),y=(a(150),function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(){return Object(u.a)(this,a),t.apply(this,arguments)}return Object(m.a)(a,[{key:"render",value:function(){return r.a.createElement("div",{className:"dayscale-row"},r.a.createElement("div",{className:"dayscale-label"},"Mon"),r.a.createElement("div",{className:"dayscale-label"},"Tue"),r.a.createElement("div",{className:"dayscale-label"},"Wed"),r.a.createElement("div",{className:"dayscale-label"},"Thu"),r.a.createElement("div",{className:"dayscale-label"},"Fri"),r.a.createElement("div",{className:"dayscale-label"},"Sat"),r.a.createElement("div",{className:"dayscale-label"},"Sun"))}}]),a}(r.a.Component)),F=function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(){return Object(u.a)(this,a),t.apply(this,arguments)}return Object(m.a)(a,[{key:"render",value:function(){return r.a.createElement("div",{className:c.isMobile?"scheduler-mobile":"scheduler-wrapper"},r.a.createElement(p.a,null,r.a.createElement(E.b,{data:this.props.coursesToDisplay},r.a.createElement(v.q,{currentDate:"2018-11-01"}),r.a.createElement(E.c,{startDayHour:7.667,endDayHour:17.5,cellDuration:60,dayScaleRowComponent:y}),r.a.createElement(E.a,null))))}}]),a}(r.a.Component),g=a(235),f=a(234),C=a(222),k=a(165),S=a(170),b=a(167),D=a(166),N=a(221),M=a(225),w=a(230),A=a(120),O=a.n(A),j=a(121),x=a.n(j),T=[{code:5710213,abbreviation:"CENG213",name:"Data Structures",category:0,sections:[{instructor:"Yusuf Sahillio\u011flu",dept:["CENG","EE"],surnameStart:"AA",surnameEnd:"FF",lectureTimes:[{classroom:"BMB-1",day:0,startHour:8,startMin:40,endHour:10,endMin:30},{classroom:"BMB-4",day:2,startHour:15,startMin:40,endHour:17,endMin:30}]},{instructor:"Cevat \u015eener",dept:["CENG","EE"],surnameStart:"FG",surnameEnd:"ZZ",lectureTimes:[{classroom:"U-3",day:2,startHour:10,startMin:40,endHour:12,endMin:30},{classroom:"CZ-14",day:6,startHour:15,startMin:40,endHour:17,endMin:30}]}]},{code:5710140,abbreviation:"CENG140",name:"C Programming",category:1,sections:[{instructor:"G\xf6kt\xfcrk \xdc\xe7oluk",dept:["CENG"],surnameStart:"AA",surnameEnd:"ZZ",lectureTimes:[{classroom:"BMB-1",day:0,startHour:8,startMin:40,endHour:10,endMin:30},{classroom:"BMB-5",day:2,startHour:15,startMin:40,endHour:17,endMin:30}]}]}];function B(){return T}var H=a(223),G=a(232),I=a(224),P=a(124),z=a(233),Z=a(226),W=a(162),q=a(227),L=a(68),R=a.n(L),J=a(81),U=a.n(J),Y=(a(151),function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(e){var n;return Object(u.a)(this,a),(n=t.call(this,e)).days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],n}return Object(m.a)(a,[{key:"formatTime",value:function(e){return e>9?e.toString():"0"+e.toString()}},{key:"getDepartmentCriteria",value:function(){for(var e="",t=0;t<this.props.sectionDetails.dept.length;t++)e+=this.props.sectionDetails.dept[t]+" ";return e}},{key:"renderTimes",value:function(){var e=this,t=Array(0);return this.props.sectionDetails.lectureTimes.map((function(a){t.push(r.a.createElement("div",{className:"section-date",style:{background:e.props.color.ternary}},r.a.createElement("div",{className:"time-row"},e.days[a.day]+" "+a.startHour+"."+e.formatTime(a.startMin)+"-"+a.endHour+"."+e.formatTime(a.endMin)),r.a.createElement("div",{className:"time-row"},"Classroom: "+a.classroom)))})),t}},{key:"render",value:function(){return r.a.createElement("div",{className:"section-info",style:{background:this.props.color.secondary}},r.a.createElement("div",null,"Section "+this.props.sectionNo),r.a.createElement(M.a,null),r.a.createElement("div",{className:"section-row"},"Instructor: "+this.props.sectionDetails.instructor),r.a.createElement("div",{className:"section-row"},"Surname: "+this.props.sectionDetails.surnameStart+"-"+this.props.sectionDetails.surnameEnd),r.a.createElement("div",{className:"section-row"},"Department: "+this.getDepartmentCriteria()),r.a.createElement("div",{className:"section-row"},this.renderTimes()))}}]),a}(r.a.Component)),$=(a(152),function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(e){var n;return Object(u.a)(this,a),(n=t.call(this,e)).state={selectedSections:Array(e.course.sections.length).fill(!0),sectionCount:e.course.sections.length},n}return Object(m.a)(a,[{key:"handleToggle",value:function(e){this.props.onToggle(e)}},{key:"toggleSections",value:function(){this.setState({selectedSections:Array(this.state.sectionCount).fill(!this.state.selectedSections[0])})}},{key:"renderCheckBoxes",value:function(){var e=this;if(this.state.sectionCount<=0)return null;for(var t=Array(0),a=function(a){t.push(r.a.createElement(H.a,{control:r.a.createElement(G.a,{checked:e.state.selectedSections[a],onChange:function(t){var n=e.state.selectedSections.slice(0);n[a]=!n[a],e.setState({selectedSections:n}),e.handleToggle(n)},color:"primary"}),label:a+1}))},n=0;n<this.state.sectionCount;n++)a(n);return r.a.createElement(I.a,{row:!0},t,r.a.createElement(N.a,{color:"primary",onClick:function(){return e.toggleSections()}},"Toggle"))}},{key:"renderSectionDetails",value:function(){for(var e=Array(0),t=0;t<this.props.course.sections.length;t++)e.push(r.a.createElement(Y,{sectionNo:t+1,sectionDetails:this.props.course.sections[t],color:this.props.color}));return e}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"course-card",style:{background:this.props.color.main}},r.a.createElement("div",{className:"course-row"},r.a.createElement(P.a,{size:"small",onClick:function(){return e.props.onDelete()}},r.a.createElement(R.a,{fontSize:"inherit"})),r.a.createElement(z.a,{style:{background:this.props.color.main}},r.a.createElement(Z.a,{expandIcon:r.a.createElement(U.a,null),"aria-controls":"panel1a-content"},r.a.createElement(W.a,{style:{color:this.props.color.text}},this.props.course.abbreviation+": "+this.props.course.name)),r.a.createElement(q.a,null,r.a.createElement("div",{className:"course-details"},r.a.createElement(M.a,null),r.a.createElement("div",{className:"course-centered-row"},r.a.createElement("div",null,"Sections")),r.a.createElement(M.a,null),r.a.createElement("div",{className:"course-row"},this.renderCheckBoxes()),r.a.createElement(M.a,null),this.renderSectionDetails())))))}}]),a}(r.a.Component)),K=a(231),Q=a(118),V=a.n(Q),X=(a(153),function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(e){var n;return Object(u.a)(this,a),(n=t.call(this,e)).state={course:null,category:-1},n}return Object(m.a)(a,[{key:"handleCourseAdd",value:function(){this.props.onCourseAdd(this.state.course),this.setState({course:null,category:-1})}},{key:"render",value:function(){var e,t,a=this;return r.a.createElement("div",{className:"add-course-wrapper"},r.a.createElement("div",{className:"add-course-row"},r.a.createElement(k.a,{className:"category-form",variant:"outlined"},r.a.createElement(b.a,{className:"category-select",value:this.state.category,onChange:function(e){return a.setState({category:e.target.value,course:null})},inputProps:{id:"category-select"}},r.a.createElement(g.a,{value:-1},"All courses"),r.a.createElement(g.a,{value:0},"Must"),r.a.createElement(g.a,{value:1},"Technical"),r.a.createElement(g.a,{value:2},"Restricted"),r.a.createElement(g.a,{value:3},"Non-Tech"))),r.a.createElement(K.a,{className:"add-course-name",options:(e=this.props.courses,t=this.state.category,t<0?e:e.filter((function(e){return e.category===t}))),getOptionLabel:function(e){return e.abbreviation+": "+e.name},style:{width:"60%"},value:this.state.course,renderInput:function(e){return r.a.createElement(C.a,Object.assign({},e,{label:"Course name",variant:"outlined"}))},onChange:function(e,t){return a.setState({course:t})}}),null!==this.state.course?r.a.createElement(P.a,{onClick:function(){return a.handleCourseAdd()}},r.a.createElement(V.a,{fontSize:"large",color:"primary"})):null))}}]),a}(r.a.Component)),_=(a(155),a(119)),ee=a.n(_),te=function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(){return Object(u.a)(this,a),t.apply(this,arguments)}return Object(m.a)(a,[{key:"handleSurnameCheck",value:function(){this.props.onSettingsChange({checkSurname:!this.props.settings.checkSurname,checkDepartment:this.props.settings.checkDepartment,checkCollision:this.props.settings.checkCollision})}},{key:"handleDepartmentCheck",value:function(){this.props.onSettingsChange({checkSurname:this.props.settings.checkSurname,checkDepartment:!this.props.settings.checkDepartment,checkCollision:this.props.settings.checkCollision})}},{key:"handleCollisionCheck",value:function(){this.props.onSettingsChange({checkSurname:this.props.settings.checkSurname,checkDepartment:this.props.settings.checkDepartment,checkCollision:!this.props.settings.checkCollision})}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:"settings-wrapper"},r.a.createElement(z.a,{style:{background:"aliceblue"}},r.a.createElement(Z.a,{expandIcon:r.a.createElement(U.a,null),"aria-controls":"panel1a-content"},r.a.createElement("div",{className:"settings-row"},r.a.createElement(ee.a,{color:"primary",fontSize:"large"}),r.a.createElement("div",{className:"settings-typo"},r.a.createElement(W.a,null,"Advanced Settings")))),r.a.createElement(q.a,null,r.a.createElement("div",{className:"settings-accordion"},r.a.createElement(M.a,null),r.a.createElement("div",{className:"settings-row"},r.a.createElement(H.a,{control:r.a.createElement(G.a,{checked:this.props.settings.checkSurname,onChange:function(){return e.handleSurnameCheck()},color:"primary"}),label:"Check surname"}),r.a.createElement(H.a,{control:r.a.createElement(G.a,{checked:this.props.settings.checkDepartment,onChange:function(){return e.handleDepartmentCheck()},color:"primary"}),label:"Check department"}),r.a.createElement(H.a,{control:r.a.createElement(G.a,{checked:this.props.settings.checkCollision,onChange:function(){return e.handleCollisionCheck()},color:"primary"}),label:"Check collision"}))))))}}]),a}(r.a.Component),ae=function(){function e(){Object(u.a)(this,e),this.colors=[{main:"#33CDE8",secondary:"#FFFFFF",ternary:"#C3F6FF",text:"#000000",textSection:"#FFFFFF"},{main:"#E293FA",secondary:"#FFFFFF",ternary:"#F7DCFF",text:"#000000",textSection:"#FFFFFF"},{main:"#FFF040",secondary:"#FFFFFF",ternary:"#F7F3C2",text:"#000000",textSection:"#FFFFFF"},{main:"#71F154",secondary:"#FFFFFF",ternary:"#DDF7D7",text:"#000000",textSection:"#FFFFFF"},{main:"#E82A2A",secondary:"#FFFFFF",ternary:"#FFA9A9",text:"#000000",textSection:"#FFFFFF"},{main:"#F1951F",secondary:"#FFFFFF",ternary:"#FFD39A",text:"#000000",textSection:"#FFFFFF"},{main:"#B59FF7",secondary:"#FFFFFF",ternary:"#E9E2FE",text:"#000000",textSection:"#FFFFFF"},{main:"#8D969A",secondary:"#FFFFFF",ternary:"#CAD2D5",text:"#000000",textSection:"#FFFFFF"}],this.iterator=-1}return Object(m.a)(e,[{key:"getNextColor",value:function(){return this.colors.length<=0?{main:0,secondary:0,ternary:0}:(this.iterator=(this.iterator+1)%this.colors.length,this.colors[this.iterator])}}]),e}(),ne=(a(156),function(e){Object(h.a)(a,e);var t=Object(d.a)(a);function a(e){var n;return Object(u.a)(this,a),(n=t.call(this,e)).state={surname:"",department:"",semester:0,alertMsg:"",errorDept:!1,errorSemester:!1,selectedCourses:[],allCourses:B(),settings:{checkSurname:!0,checkDepartment:!0,checkCollision:!0},scenarios:[],colorset:new ae},n}return Object(m.a)(a,[{key:"componentDidMount",value:function(){document.title="Robot De\u011filim *-*",c.isMobile&&(document.body.style.zoom="60%")}},{key:"getCourseByCode",value:function(e){for(var t=0;t<this.state.allCourses.length;t++)if(this.state.allCourses[t].code===e)return this.state.allCourses[t];return null}},{key:"renderSemesterSelections",value:function(e){var t=Array(0);t.push(r.a.createElement(g.a,{value:0},"---"));for(var a=0;a<e;a++)t.push(r.a.createElement(g.a,{value:a+1},a+1));return t}},{key:"handleAddMustCourse",value:function(){this.setState({alertMsg:"",errorDept:!1,errorSemester:!1}),this.state.department.length<2?this.setState({alertMsg:"Please enter a correct department",errorDept:!0}):this.state.semester<1&&this.setState({alertMsg:"Please choose a semester",errorSemester:!0})}},{key:"handleAlertClose",value:function(){this.setState({alertMsg:""})}},{key:"handleDeleteCourse",value:function(e){var t=this.state.selectedCourses.slice(0);t[e]=null,this.setState({selectedCourses:t})}},{key:"handleToggle",value:function(e,t){var a=this.state.selectedCourses.slice(0);a[e].sections=t,this.setState({selectedCourses:a}),console.log("Course "+e+" sections:"+t)}},{key:"handleAddCourse",value:function(e){var t=this.state.selectedCourses.slice(0);t.push({code:e.code,sections:Array(e.sections.length).fill(!0),color:this.state.colorset.getNextColor()}),this.setState({selectedCourses:t})}},{key:"handleChangeSettings",value:function(e){this.setState({settings:e})}},{key:"handleScheduleBegin",value:function(){var e=this;Array(0);this.state.selectedCourses.map((function(t){e.getCourseByCode(t.code)}))}},{key:"render",value:function(){var e=this;return r.a.createElement("div",{className:c.isMobile?"control-mobile":"control-wrapper"},r.a.createElement(f.a,{open:""!==this.state.alertMsg,autoHideDuration:5e3,onClose:function(){return e.handleAlertClose()}},r.a.createElement(w.a,{elevation:6,variant:"filled",onClose:function(){return e.handleAlertClose()},severity:"error"},this.state.alertMsg)),r.a.createElement("div",{className:"control-row"},r.a.createElement("div",{className:"textfield-wrapper"},r.a.createElement(C.a,{required:!0,label:"Surname",value:this.state.surname,inputProps:{maxLength:12},variant:"outlined",onChange:function(t){return e.setState({surname:t.target.value})}})),r.a.createElement("div",{className:"textfield-wrapper"},r.a.createElement(C.a,{required:!0,error:this.state.errorDept,label:"Department",value:this.state.department,inputProps:{maxLength:12},variant:"outlined",onChange:function(t){return e.setState({department:t.target.value})}}))),r.a.createElement("div",{className:"control-row"},r.a.createElement("div",{className:"textfield-wrapper"},r.a.createElement(k.a,{className:"form-control"},r.a.createElement(S.a,null,"Semester"),r.a.createElement(b.a,{error:this.state.errorSemester,value:this.state.semester,onChange:function(t){return e.setState({semester:t.target.value})}},this.renderSemesterSelections(8)),r.a.createElement(D.a,null,"Ex: 2nd year Fall semester -> 3"))),r.a.createElement("div",{className:"control-button"},r.a.createElement(N.a,{variant:"contained",color:"secondary",startIcon:r.a.createElement(O.a,null),onClick:function(){return e.handleAddMustCourse()}},"Add Must Courses")),r.a.createElement("div",{className:"control-button"},r.a.createElement(N.a,{variant:"contained",color:"primary",startIcon:r.a.createElement(x.a,null),onClick:function(){return e.handleScheduleBegin()}},"Schedule"))),r.a.createElement(te,{settings:this.state.settings,onSettingsChange:function(t){return e.handleChangeSettings(t)}}),r.a.createElement(M.a,null),r.a.createElement("div",{className:"control-row"},r.a.createElement("div",{className:"centered-row"},"Added Courses")),r.a.createElement(M.a,null),this.state.selectedCourses.map((function(t,a){return null!==t?r.a.createElement($,{course:e.getCourseByCode(t.code),onDelete:function(){return e.handleDeleteCourse(a)},onToggle:function(t){return e.handleToggle(a,t)},color:t.color}):null})),r.a.createElement(X,{courses:this.state.allCourses,onCourseAdd:function(t){return e.handleAddCourse(t)}}))}}]),a}(r.a.Component)),re=[{startDate:"2018-11-01T09:40",endDate:"2018-11-01T11:30",title:"Meeting"},{startDate:"2018-11-01T12:00",endDate:"2018-11-01T13:30",title:"Go to a gym"},{startDate:"2018-11-02T09:40",endDate:"2018-11-02T11:30",title:"Meeting"}];a(157);var se=Object(l.a)({palette:{secondary:{main:"#71F154"}}});var oe=function(){return r.a.createElement(i.a,{theme:se},r.a.createElement("div",{className:"App"},r.a.createElement("div",{className:c.isMobile?"column":"row"},r.a.createElement(F,{coursesToDisplay:re}),r.a.createElement(ne,null))))};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));o.a.render(r.a.createElement(r.a.StrictMode,null,r.a.createElement(oe,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[138,1,2]]]);
//# sourceMappingURL=main.b3e2ff98.chunk.js.map