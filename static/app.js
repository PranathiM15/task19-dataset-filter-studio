function loadExample(kind){
  const form=document.createElement('form');form.method='post';
  form.innerHTML='<input name="action" value="dataset"><input name="dataset_kind" value="'+kind+'">';
  document.body.appendChild(form);form.submit();
}
function fillExample(){ setPreset('score'); }
function setPreset(which){
  const cols=[...document.querySelectorAll('.column-select')];
  const ops=[...document.querySelectorAll('.operator-select')];
  const vals=[...document.querySelectorAll('.value-field')];
  cols.forEach(x=>x.value=''); vals.forEach(x=>{x.value='';x.disabled=false});
  if(which==='score'){
    const i=0; cols[i].value=cols[i].querySelector('option[value="Score"]')?'Score':'Fare';
    ops[i].value='greater_equal'; vals[i].value=cols[i].value==='Score'?'75':'50';
  } else if(which==='attendance'){
    const i=0; cols[i].value=cols[i].querySelector('option[value="Attendance"]')?'Attendance':'Age';
    ops[i].value='greater_equal'; vals[i].value=cols[i].value==='Attendance'?'85':'30';
  } else {
    const i=0; cols[i].value=cols[i].querySelector('option[value="Student"]')?'Student':'Name';
    ops[i].value='contains'; vals[i].value='a';
  }
  document.querySelector('select[name="joiner"]').value='AND';
  document.getElementById('filter-form').requestSubmit();
}
document.querySelectorAll('.operator-select').forEach((select)=>{
  select.addEventListener('change',()=>{
    const value=select.closest('.rule-row').querySelector('.value-field');
    value.disabled=['is_empty','is_not_empty'].includes(select.value);
    if(value.disabled)value.value='';
  });
});
