"""Exercise install.sh rsync exclusions in an isolated temporary directory."""
import pathlib,re,subprocess,tempfile
script=pathlib.Path('/home/voron/printer_data/config/scripts/install.sh').read_text()
block=script.split('rsync -a --delete --itemize-changes',1)[1].split('"${SOURCE_CONFIG_DIR}/"',1)[0]
excludes=re.findall(r'--exclude "([^"]+)"',block)
with tempfile.TemporaryDirectory(prefix='tkc-filter-check-') as work:
    base=pathlib.Path(work); src=base/'source'; dst=base/'destination'
    for root in (src,dst): (root/'tool_calibrator/backups').mkdir(parents=True)
    (src/'tool_calibrator/tool_offsets.cfg').write_text('repository seed')
    (dst/'tool_calibrator/tool_offsets.cfg').write_text('measured machine offsets')
    (dst/'tool_calibrator/backups/keep.cfg').write_text('keep backup')
    (dst/'.tool_calibrator_manifest.json').write_text('keep manifest')
    (src/'tool_calibrator/tool_calibrator.cfg').write_text('new master config')
    cmd=['rsync','-a','--delete']
    for pattern in excludes: cmd+=['--exclude',pattern]
    subprocess.run(cmd+[str(src)+'/',str(dst)+'/'],check=True)
    assert (dst/'tool_calibrator/tool_offsets.cfg').read_text()=='measured machine offsets'
    assert (dst/'tool_calibrator/backups/keep.cfg').read_text()=='keep backup'
    assert (dst/'.tool_calibrator_manifest.json').read_text()=='keep manifest'
    assert (dst/'tool_calibrator/tool_calibrator.cfg').read_text()=='new master config'
print('PASS: actual rsync filters preserve machine offsets, backups and manifest; master config deploys.')
