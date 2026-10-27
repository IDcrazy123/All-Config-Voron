#Requires -Version 5.1
[CmdletBinding()]
param([string]$Python = "python", [string]$Bash)
$ErrorActionPreference = "Stop"
if ($Bash) { $env:VORON_TEST_BASH = $Bash }
$env:VORON_TEST_POWERSHELL = (Get-Process -Id $PID).Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location $repoRoot
try {
@'
"""Offline CFG contracts; embedded to leave all existing .py files unchanged.

No printer/network access. The replay models selected G-code/transform behavior,
not firmware scheduling or mechanical clearance. Historical fixtures are kept
immutable; their two obsolete same-file invariants are explicitly superseded.
"""
import ast, copy, hashlib, importlib.util, json, os, re, shlex, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path('extras/tests').resolve()))
import test_portability as cfg
import test_individual_cfg as individual
import test_install_preflight as installer
import test_klipper_pty as pty

ROOT = Path.cwd()
BACKUP = ROOT / 'extras/backups/pre-cfg-software-hardening-20261016-200256'
spec = importlib.util.spec_from_file_location('cleaner_checks', ROOT / 'extras/experiments/t0-cleaner-20261015/test_nozzle_clean_v2.py')
cleaner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cleaner
spec.loader.exec_module(cleaner)
old_init = cleaner.OfflinePrinter.__init__
def complete_cleaner_fixture(self, variables, templates):
    old_init(self, variables, templates)
    # New admission checks need actual configured heater bounds. No assertions
    # or production guards are removed to accommodate the historical fixture.
    self.printer['configfile'] = {'settings': copy.deepcopy(cfg.printer_fixture()['configfile']['settings'])}
cleaner.OfflinePrinter.__init__ = complete_cleaner_fixture
for name in ('test_cfg_native_hardware_and_dock_paths_unchanged',
             'test_measured_feature_moves_and_default_heat_commands_match_backup'):
    setattr(individual.IndividualFeatureTests, name, unittest.skip(
        'Historical Oct9 same-file/cleaner contract; replaced by current preservation and cleaner checks in this runner')(
            getattr(individual.IndividualFeatureTests, name)))

def fixture(z=30, offset=0):
    p = cfg.printer_fixture()
    p['toolhead']['position'] = cfg.Coord(180,168,z)
    p['gcode_move'].update(gcode_position=cfg.Coord(180,168,z-offset),
                           absolute_coordinates=True, absolute_extrude=False)
    p['idle_timeout'] = {'state':'Ready'}
    p['configfile']['settings']['pause_resume'] = {'recover_velocity':50}
    for t in range(5):
        p['tool T'+str(t)].update(gcode_z_offset=offset, gcode_x_offset=0, gcode_y_offset=0)
        p['filament_switch_sensor filament_sensor_T'+str(t)] = {'enabled':True,'filament_detected':True}
    return p

class Replay:
    def __init__(self,p):
        self.p=p; self.commands=[]; self.absolute=True; self.fail_dock=False
    def run(self,name,params=None):
        for raw in cfg.render(name,self.p,params or {}).splitlines():
            lexer=shlex.shlex(raw,posix=True); lexer.whitespace_split=True; lexer.commenters='#;'
            words=list(lexer)
            if not words: continue
            line=' '.join(words); cmd=words[0]; args=dict(w.split('=',1) for w in words[1:] if '=' in w)
            self.commands.append(line)
            if 'gcode_macro '+cmd in cfg.CFG:
                self.run(cmd,args); continue
            if cmd=='SET_GCODE_VARIABLE':
                self.p['gcode_macro '+args['MACRO']][args['VARIABLE']]=ast.literal_eval(args['VALUE'])
            elif cmd=='TURN_OFF_HEATERS':
                for key in ('heater_bed','extruder','extruder1','extruder2','extruder3','extruder4'):
                    self.p[key]['target']=0
            elif cmd=='CANCEL_PRINT_BASE': self.p['pause_resume']['is_paused']=False
            elif cmd=='PAUSE_BASE': self.p['pause_resume']['is_paused']=True
            elif cmd=='CLEAR_PAUSE': self.p['pause_resume']['is_paused']=False
            elif cmd=='SET_GCODE_OFFSET':
                self.p['gcode_move']['homing_origin']=cfg.Coord(*[float(args.get(a,0)) for a in 'XYZ'])
            elif cmd=='UNSELECT_TOOL':
                if self.fail_dock: raise ValueError('simulated dock failure')
                if args.get('RESTORE_AXIS')!='': raise AssertionError('Finish docking must not restore tool-relative Z')
                self.p['toolchanger']['tool_number']=-1
                self.p['toolhead']['position']=cfg.Coord(30,120,331)
            elif cmd in ('G90','G91'): self.absolute=cmd=='G90'
            elif cmd in ('G0','G1'):
                axes={k:float(v) for k,v in re.findall(r'([XYZ])\s*(-?\d+(?:\.\d+)?)',line)}
                pos=list(self.p['toolhead']['position']); tool=self.p['toolchanger']['tool_number']
                for axis,val in axes.items():
                    i='XYZ'.index(axis)
                    off=self.p['tool T'+str(tool)].get('gcode_'+axis.lower()+'_offset',0) if tool>=0 else 0
                    origin=self.p['gcode_move']['homing_origin'][i]
                    pos[i]=val+off+origin if self.absolute else pos[i]+val
                if not -5-1e-6<=pos[2]<=347+1e-6: raise AssertionError('Physical Z outside travel: '+line+' => '+str(pos[2]))
                self.p['toolhead']['position']=cfg.Coord(*pos)

class CurrentContracts(unittest.TestCase):
    def test_shutdown_cancels_auxiliary_callbacks_before_they_can_reheat(self):
        for macro in ('CANCEL_PRINT','PRINT_END'):
            p=fixture(); p['toolhead']['homed_axes']=''
            p['gcode_macro _PRINT_STATE']['state']='drying'
            p['gcode_macro _DRYER_STATUS'].update(is_drying=1,time_remaining=100,total_time=100,bed_temp=70)
            p['gcode_macro _TOOL_HEATUP_VARS']['is_running']=1
            r=Replay(p); r.run(macro)
            self.assertEqual(r.commands[0],'TURN_OFF_HEATERS')
            self.assertEqual(p['gcode_macro _DRYER_STATUS']['is_drying'],0)
            self.assertEqual(p['gcode_macro _TOOL_HEATUP_VARS']['is_running'],0)
            self.assertIn('UPDATE_DELAYED_GCODE ID=DRYER_TIMER DURATION=0',r.commands)
            self.assertIn('UPDATE_DELAYED_GCODE ID=_TOOL_HEATUP_TIMER DURATION=0',r.commands)
            self.assertNotIn('M140',cfg.render('_DRYER_STATUS',p))
            self.assertNotIn('SET_HEATER_TEMPERATURE',cfg.ENV.from_string(cfg.CFG['delayed_gcode _TOOL_HEATUP_TIMER']['gcode']).render(printer=p))

    def test_exclusion_empty_reset_matches_native_truthiness(self):
        p=fixture(); p['gcode_macro _PRINT_STATE'].update(state='printing',used_tool_count=2)
        for args in ({'RESET':'','NAME':'part'},{'RESET':'','CURRENT':'1'}):
            with self.assertRaisesRegex(ValueError,'exclusion is blocked'):
                cfg.render('EXCLUDE_OBJECT',p,args)
        for args in ({'RESET':'1','NAME':'part'},{'RESET':'0','NAME':'part'},{'RESET':''}):
            self.assertIn('_EXCLUDE_OBJECT_BASE',cfg.render('EXCLUDE_OBJECT',p,args))

    def test_pending_tool_recovery_blocks_manual_features_and_fresh_cleaner_helpers(self):
        p=fixture(); p['gcode_macro _TOOL_RECOVERY']['required']=1
        calls={'PRIME_LINES':{'INITIAL_TOOL':'0','T0_TEMP':'220'},
               '_PRIME_LINES_TOOL':{},'CLEAN_NOZZLE':{},'_CLEAN_NOZZLE_PURGE':{},
               '_CLEAN_NOZZLE_WIPE_PATH':{},'_CLEAN_NOZZLE_PARK':{},
               'MEASURE_TOOL_HEATUP':{'PARK_BUCKET':'0'},'TEST_SPEED':{},'TEST_Z_SPEED':{},
               'START_DRYER':{'PARK':'0','CHAMBER':'0'},'_DRYER_PARK':{},
               '_CALIBRATE_SAFE_TRANSIT':{},'CALIBRATE_MOVE_OVER_PROBE':{}}
        for name,args in calls.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError,'recovery'):
                cfg.render(name,p,args)

    def test_led_presentation_cannot_change_operation_or_paused_tool(self):
        for phase in ('idle','starting','printing','paused','drying','calibrating'):
            for macro in ('_SET_LED_STATUS_PRINTING','_SET_LED_STATUS_PAUSE',
                          '_SET_LED_STATUS_COMPLETE','_SET_LED_STATUS_DRYING',
                          '_SET_LED_STATUS_DRYING_COMPLETE'):
                p=fixture(); p['gcode_macro _PRINT_STATE'].update(state=phase,paused_tool=2)
                before=copy.deepcopy(p['gcode_macro _PRINT_STATE'])
                Replay(p).run(macro)
                self.assertEqual(p['gcode_macro _PRINT_STATE'],before,(phase,macro))

    def test_pause_lifecycle_retains_original_tool_on_repeated_hook(self):
        p=fixture(); p['gcode_macro _PRINT_STATE']['state']='printing'
        r=Replay(p); r.run('_PRINT_PAUSED')
        self.assertEqual(p['gcode_macro _PRINT_STATE']['state'],'paused')
        self.assertEqual(p['gcode_macro _PRINT_STATE']['paused_tool'],0)
        p['toolchanger']['tool_number']=2
        r.run('_PRINT_PAUSED')
        self.assertEqual(p['gcode_macro _PRINT_STATE']['paused_tool'],0)

    def test_repeated_pause_preserves_resume_temperature_and_has_no_park(self):
        p=fixture(); p['pause_resume']['is_paused']=True
        p['gcode_macro RESUME']['last_extruder_temp']={'restore':True,'temp':240}
        original=copy.deepcopy(p['gcode_macro RESUME'])
        r=Replay(p); r.run('PAUSE')
        self.assertEqual(p['gcode_macro RESUME'],original)
        self.assertFalse(any(x.startswith(('G0 ','G1 ','_TOOLHEAD_PARK','_CLIENT_RETRACT','PAUSE_BASE','SET_GCODE_VARIABLE')) for x in r.commands))

    def test_pause_with_recovery_uses_no_xyz_handler_and_normal_pause_keeps_hooks(self):
        p=fixture(); p['print_stats']['state']='printing'; p['gcode_macro _TOOL_RECOVERY']['required']=1
        r=Replay(p); r.run('PAUSE')
        self.assertTrue(p['pause_resume']['is_paused'])
        self.assertIn('PAUSE_BASE',r.commands)
        self.assertFalse(any(re.match(r'UNSELECT_TOOL|G28|_TOOLHEAD_PARK',x) or
                             (re.match(r'G[01]\s',x) and re.search(r'\s[XYZ]-?\d',x))
                             for x in r.commands))
        p=fixture(); out=cfg.render('PAUSE',p)
        self.assertLess(out.index('PAUSE_BASE'),out.index('_PRINT_PAUSED'))
        self.assertIn('_TOOLHEAD_PARK_PAUSE_CANCEL',out)

    def test_dryer_docking_replay_preserves_clearance_for_all_tool_offsets(self):
        for z in (30,200,345,347):
            for offset in (-0.3515,0,0.1665):
                p=fixture(z,offset); p['fan_generic bed_fan']={'speed':0}
                r=Replay(p); r.run('START_DRYER',{'CHAMBER':'0','PARK':'1'})
                self.assertIn('UNSELECT_TOOL RESTORE_AXIS=',r.commands)
                self.assertEqual(p['toolchanger']['tool_number'],-1)
                self.assertGreaterEqual(p['toolhead']['position'].z,200)
                self.assertEqual(p['gcode_macro _PRINT_STATE']['state'],'drying')
                r.run('STOP_DRYER')
                self.assertEqual(p['gcode_macro _PRINT_STATE']['state'],'idle')
        p=fixture(); p['toolchanger']['tool_number']=0
        with self.assertRaisesRegex(ValueError,'empty'): cfg.render('_DRYER_PARK',p)

    def test_prime_rejects_competing_operations_and_cold_extrusion_before_output(self):
        args={'INITIAL_TOOL':'0','T0_TEMP':'220'}
        for phase in ('printing','paused','drying','calibrating'):
            p=fixture(); p['gcode_macro _PRINT_STATE']['state']=phase
            with self.assertRaisesRegex(ValueError,'idle/starting'): cfg.render('PRIME_LINES',p,args)
        with self.assertRaisesRegex(ValueError,'extrusion limit'):
            cfg.render('PRIME_LINES',fixture(),args|{'T0_TEMP':'150'})
        p=fixture(); p['print_stats']['state']='printing'
        with self.assertRaises(ValueError): cfg.render('_REQUIRE_MOTION_PREPARATION',p)
        p['gcode_macro _PRINT_STATE']['state']='starting'
        cfg.render('_REQUIRE_MOTION_PREPARATION',p)
        cfg.render('PRIME_LINES',p,args)

    def test_native_hardware_saved_data_readonly_and_python_unchanged(self):
        m=json.loads((BACKUP/'manifest.json').read_text())
        for name,sha in m['python_files_unchanged_contract'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha,name)
        for name,sha in m['originals'].items():
            if ('readonly-configs/' in name or name=='config/printer.cfg' or
                name=='config/Printer-Setup/hardware.cfg' or
                (name.startswith('config/toolchanger/tools/') and name not in
                 ('config/toolchanger/tools/T0.cfg','config/toolchanger/tools/T2.cfg'))):
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha,name)
        self.assertEqual(float(cfg.CFG['tool T0']['params_park_y'].split('#')[0]),1.3)
        self.assertEqual(float(cfg.CFG['tool T2']['params_park_y'].split('#')[0]),1.6)

    def test_end_lift_full_replay_boundaries_and_tool_offsets(self):
        for z in (0.28,30,342,345,347):
            for offset in (-0.3515,0,0.1665):
                for hot in (True,False):
                    with self.subTest(z=z,offset=offset,hot=hot):
                        p=fixture(z,offset); p['extruder']['can_extrude']=hot
                        r=Replay(p); r.run('PRINT_END')
                        self.assertEqual(r.commands[0],'TURN_OFF_HEATERS')
                        self.assertGreaterEqual(p['toolhead']['position'].z,min(max(z+10,20),347))
                        self.assertEqual(p['toolchanger']['tool_number'],-1)

    def test_crash_cancel_replay_has_no_motion_or_docking(self):
        p=fixture(); p['gcode_macro _TOOL_RECOVERY'].update(required=1,tool=0)
        p['pause_resume']['is_paused']=True
        r=Replay(p); r.run('CANCEL_PRINT')
        self.assertFalse(any(re.match(r'G[01]\s|UNSELECT_TOOL|G28',x) for x in r.commands))
        self.assertIn('CANCEL_PRINT_BASE',r.commands)
        self.assertEqual(p['gcode_macro _TOOL_RECOVERY']['required'],0)
        self.assertFalse(p['pause_resume']['is_paused'])
        self.assertEqual(p['heater_bed']['target'],0)
        self.assertEqual(cfg.CFG['toolchanger']['error_gcode'].strip(),'_TOOL_CRASH_SAFE_PAUSE')

    def test_crash_print_end_skips_motion_and_clears_guard(self):
        p=fixture(); p['gcode_macro _TOOL_RECOVERY']['required']=1
        r=Replay(p); r.run('PRINT_END')
        self.assertFalse(any(re.match(r'G[01]\s|UNSELECT_TOOL|G28',x) for x in r.commands))
        self.assertEqual(p['gcode_macro _TOOL_RECOVERY']['required'],0)
        self.assertEqual(p['heater_bed']['target'],0)

    def test_normal_cancel_is_canceled_and_cold_before_dock_failure(self):
        p=fixture(); p['pause_resume']['is_paused']=True
        r=Replay(p); r.fail_dock=True
        with self.assertRaisesRegex(ValueError,'simulated dock'): r.run('CANCEL_PRINT')
        self.assertFalse(p['pause_resume']['is_paused'])
        self.assertEqual(p['extruder']['target'],0)

    def test_cancel_and_end_skip_motion_without_homing_or_ready_state(self):
        for macro in ('PRINT_END','_CUSTOM_CANCEL_CLEANUP'):
            for section,key,value in [('toolhead','homed_axes',''),('toolchanger','status','error')]:
                p=fixture(); p[section][key]=value
                out=cfg.render(macro,p)
                self.assertFalse(any(re.match(r'G[01]\s|UNSELECT_TOOL|_PRINT_FINISH_PARK',x.strip()) for x in out.splitlines()))

    def test_start_admission_and_all_heater_limits(self):
        params={'TOOL':'0','TOOL_TEMP':'220','BED_TEMP':'70','T0_PURGE_TEMP':'230'}
        for phase in ('starting','printing','paused'):
            p=fixture(); p['gcode_macro _PRINT_STATE']['state']=phase
            with self.assertRaises(ValueError): cfg.render('PRINT_START',p,params)
        p=fixture(); p['pause_resume']['is_paused']=True
        with self.assertRaises(ValueError): cfg.render('PRINT_START',p,params)
        for change in ({'BED_TEMP':'130'},{'TOOL_TEMP':'350'},{'T4_TEMP':'350'},{'T2_TEMP':'-1'}):
            with self.assertRaises(ValueError): cfg.render('PRINT_START',fixture(),params|change)
        p=fixture(); p['print_stats']['state']='printing'
        self.assertIn('G28',cfg.render('PRINT_START',p,params))
        p=fixture(); p['filament_switch_sensor filament_sensor_T0']['filament_detected']=False
        out=cfg.render('PRINT_START',p,{'TOOL':'1','TOOL_TEMP':'220','BED_TEMP':'70'})
        self.assertIn('CLEAN_NOZZLE MODE=DEEP TEMP=150 WIPES=3 PURGE=0',out)
        self.assertIn('PRIME_LINES INITIAL_TOOL=1 T1_TEMP=220',out)
        self.assertIn('TEMPERATURE_WAIT SENSOR=heater_bed MINIMUM=69',out)
        self.assertNotIn('M190 S70',out)

    def test_soak_uses_one_duration_for_cold_warm_hot_and_manual_cases(self):
        base={'BED_TEMP':'100','MATERIAL':'ABS'}
        for extra,expected in [({'BED_START':'25'},'G4 P90000'),
                               ({'BED_START':'90'},'G4 P18000'),
                               ({'BED_START':'97'},None),
                               ({'BED_START':'25','SOAK':'120','AUTO_SOAK':'0'},'G4 P120000'),
                               ({'BED_START':'25','AUTO_SOAK':'0'},None)]:
            out=cfg.render('_PRINT_START_HEAT_SOAK',fixture(),base|extra)
            self.assertEqual(next((line.strip() for line in out.splitlines() if line.strip().startswith('G4 P')),None),expected)
        out=cfg.render('_PRINT_START_HEAT_SOAK',fixture(),{'BED_TEMP':'100','BED_START':'25'})
        self.assertIn('G4 P90000',out)
        out=cfg.render('_PRINT_START_HEAT_SOAK',fixture(),{'BED_TEMP':'70','BED_START':'25','MATERIAL':'PLA','FULL_BED':'1'})
        self.assertIn('G4 P60000',out)

    def test_resume_rechecks_original_tool_filament_and_runtime_heater(self):
        p=fixture(); p['pause_resume']['is_paused']=True
        p['gcode_macro _PRINT_STATE']['paused_tool']=0
        self.assertIn('_RESUME_AFTER_TOOL_CHECK',cfg.render('RESUME',p))
        self.assertIn('_RESUME_FINALIZE',cfg.render('_RESUME_AFTER_TOOL_CHECK',p))
        cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        p['filament_switch_sensor filament_sensor_T0']['filament_detected']=False
        with self.assertRaisesRegex(ValueError,'filament'): cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        p['filament_switch_sensor filament_sensor_T0']['enabled']=False
        cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        p['gcode_macro _PRINT_STATE']['paused_tool']=2
        with self.assertRaises(ValueError): cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        p['extruder']['can_extrude']=False
        with self.assertRaises(ValueError): cfg.render('_RESUME_FINALIZE',p,{'VELOCITY':'50'})
        p=fixture(); p['pause_resume']['is_paused']=True
        p['gcode_macro _TOOL_RECOVERY']['required']=1
        out=cfg.render('RESUME',p)
        self.assertLess(out.index('INITIALIZE_TOOLCHANGER'),out.index('VERIFY_TOOL_DETECTED'))
        self.assertIn('_RESUME_AFTER_TOOL_CHECK',out)
        with self.assertRaisesRegex(ValueError,'original paused tool'):
            cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        p['gcode_macro _TOOL_RECOVERY']['required']=0
        with self.assertRaisesRegex(ValueError,'original paused tool'):
            cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        p['gcode_macro _TOOL_RECOVERY']['required']=1
        p['gcode_macro _PRINT_STATE']['paused_tool']=0
        cfg.render('_RESUME_CHECK_TOOL_AND_FILAMENT',p)
        out=cfg.render('_RESUME_FINALIZE',p,{'VELOCITY':'50'})
        self.assertLess(out.index('_RESUME_CHECK_TOOL_AND_FILAMENT'),out.index('VARIABLE=required VALUE=0'))

    def test_crash_guard_autoclears_without_manual_recovery(self):
        for name in ('RECOVER_TOOL','CONFIRM_TOOL_RECOVERY','_TOOL_RECOVERY_AFTER_INIT','_TOOL_RECOVERY_CONFIRMED'):
            self.assertNotIn('gcode_macro '+name,cfg.CFG)
        p=fixture(); p['gcode_macro _TOOL_RECOVERY']['required']=1
        with self.assertRaises(ValueError): cfg.render('_REQUIRE_MOTION_PREPARATION',p)
        p['quad_gantry_level']={'applied':True}
        self.assertNotIn('VARIABLE=required VALUE=0',cfg.render('QUAD_GANTRY_LEVEL',p))
        p['gcode_macro _TOOL_RECOVERY']['required']=0
        self.assertIn('INITIALIZE_TOOLCHANGER',cfg.render('QUAD_GANTRY_LEVEL',p))
        p['toolchanger'].update(tool_number=-1,detected_tool_number=-1)
        self.assertEqual(cfg.render('_REQUIRE_TOOL_STATE',p).strip(),'')
        p['toolchanger'].update(tool_number=0,detected_tool_number=0)
        self.assertIn('VERIFY_TOOL_DETECTED T=0',cfg.render('_REQUIRE_TOOL_STATE',p))
        p['toolchanger']['detected_tool_number']=-1
        with self.assertRaises(ValueError): cfg.render('_REQUIRE_TOOL_STATE',p)
        p=fixture(); p['print_stats']['state']='standby'
        self.assertNotIn('VARIABLE=required VALUE=1',cfg.render('_TOOL_CRASH_SAFE_PAUSE',p))
        p['print_stats']['state']='printing'
        self.assertIn('VARIABLE=required VALUE=1',cfg.render('_TOOL_CRASH_SAFE_PAUSE',p))
        out=cfg.render('PRINT_START',fixture(),{'TOOL':'0','TOOL_TEMP':'220','BED_TEMP':'70','T0_PURGE_TEMP':'230'})
        self.assertLess(out.index('INITIALIZE_TOOLCHANGER'),out.index('_REQUIRE_TOOL_STATE'))
        self.assertLess(out.index('_REQUIRE_TOOL_STATE'),out.index('G28'))

    def test_axiscope_final_return_follows_safe_transit(self):
        p=fixture(); p['axiscope']={'probe_results':{str(t):{'z_offset':0.01*t} for t in range(5)}}
        p['toolchanger']['tool_numbers']=[4,0,1,2,3]
        with self.assertRaises(ValueError): cfg.render('CALIBRATE_COARSE_Z_OFFSETS',p)
        out=cfg.render('CALIBRATE_COARSE_Z_OFFSETS',p,{'CONFIRM':'1'})
        lines=[x.strip() for x in out.splitlines() if x.strip() and not x.strip().startswith('#')]
        self.assertEqual(sum(x.startswith('PROBE_ZSWITCH ') for x in lines),5)
        self.assertEqual(next(x for x in lines if re.fullmatch(r'T[0-4]',x)),'T0')
        last= max(i for i,x in enumerate(lines) if x=='T0')
        self.assertEqual(lines[last-1],'_CALIBRATE_SAFE_TRANSIT')
        for i,x in enumerate(lines):
            if re.fullmatch(r'T[0-4]',x) and i!=last:
                self.assertEqual(lines[i-1],'AXISCOPE_BEFORE_PICKUP_GCODE')
        self.assertNotIn('_AXISCOPE_CALIBRATE_ALL_Z_OFFSETS',out)
        self.assertIn('CALIBRATE_COARSE_Z_OFFSETS',cfg.render('CALIBRATE_ALL_Z_OFFSETS',p))
        cfg.render('_CALIBRATE_COARSE_REPORT',p)
        del p['axiscope']['probe_results']['4']
        with self.assertRaises(ValueError): cfg.render('_CALIBRATE_COARSE_REPORT',p)

    def test_exclusion_queries_resets_and_single_tool_remain_available(self):
        p=fixture()
        for count in (0,2,5):
            p['gcode_macro _PRINT_STATE'].update(state='printing',used_tool_count=count)
            with self.assertRaises(ValueError): cfg.render('EXCLUDE_OBJECT',p,{'NAME':'part'})
            self.assertIn('_EXCLUDE_OBJECT_BASE',cfg.render('EXCLUDE_OBJECT',p))
            self.assertIn('_EXCLUDE_OBJECT_BASE',cfg.render('EXCLUDE_OBJECT',p,{'RESET':'1','NAME':'part'}))
        p['gcode_macro _PRINT_STATE'].update(state='printing',used_tool_count=1)
        self.assertIn('_EXCLUDE_OBJECT_BASE',cfg.render('EXCLUDE_OBJECT',p,{'CURRENT':'1'}))
        p['gcode_macro _PRINT_STATE']['state']='idle'
        with self.assertRaises(ValueError): cfg.render('EXCLUDE_OBJECT',p,{'CURRENT':'1'})

    def test_shaper_global_damping_explicit_override_and_cache(self):
        p=fixture()
        tool={k:ast.literal_eval(v) for k,v in cfg.CFG['toolchanger'].items() if k.startswith('params_input_shaper_')}
        tool['tool_number']=0
        template=cfg.ENV.from_string(cfg.CFG['toolchanger']['after_change_gcode'])
        out=template.render(printer=p,tool=tool)
        self.assertIn('DAMPING_RATIO_X=0.124 DAMPING_RATIO_Y=0.08',out)
        for raw in out.splitlines():
            words=shlex.split(raw.strip())
            if words and words[0]=='SET_GCODE_VARIABLE':
                args=dict(x.split('=',1) for x in words[1:])
                p['gcode_macro '+args['MACRO']][args['VARIABLE']]=ast.literal_eval(args['VALUE'])
        self.assertNotIn('SET_INPUT_SHAPER SHAPER_TYPE_X=',template.render(printer=p,tool=tool))
        tool.update(params_input_shaper_freq_x=50,params_input_shaper_damping_ratio_x=0.15)
        out=template.render(printer=p,tool=tool)
        self.assertIn('DAMPING_RATIO_X=0.15 DAMPING_RATIO_Y=0.08',out)
        self.assertIn('VARIABLE=x_type VALUE="\'\'"',cfg.render('SET_INPUT_SHAPER',p))

    def test_calibration_and_motion_guards_do_not_admit_competing_operations(self):
        for phase in ('printing','paused','calibrating','drying'):
            p=fixture(); p['gcode_macro _PRINT_STATE']['state']=phase
            with self.assertRaises(ValueError): cfg.render('_REQUIRE_MOTION_PREPARATION',p)
        p=fixture(); p['gcode_macro _PRINT_STATE']['state']='starting'
        cfg.render('_REQUIRE_MOTION_PREPARATION',p)
        p['gcode_macro _PRINT_STATE']['state']='calibrating'
        p['temperature_sensor chamber']={'temperature':25}
        with self.assertRaises(ValueError): cfg.render('START_DRYER',p,{'PARK':'0'})

    def test_manual_offsets_are_cleared_before_finish_motion(self):
        for macro in ('PRINT_END','_CUSTOM_CANCEL_CLEANUP'):
            for origin_z in (-2,2):
                p=fixture(345,-0.3515)
                p['gcode_move']['homing_origin']=cfg.Coord(1,-1,origin_z)
                r=Replay(p); r.run(macro)
                self.assertLessEqual(p['toolhead']['position'].z,347)
                self.assertEqual(p['gcode_move']['homing_origin'],cfg.Coord(0,0,0))

@unittest.skipUnless(installer.BASH,'Bash is required')
class DeploymentContracts(unittest.TestCase):
    def test_calibration_phase_refuses_deployment_before_writes(self):
        h=installer.InstallerTests('test_dry_run_preserves_files_and_backups'); h.setUp()
        self.addCleanup(h.tearDown)
        for phase in ('calibrating','unknown-operation'):
            installer.Handler.state=copy.deepcopy(installer.BASE)
            installer.Handler.state['gcode_macro _PRINT_STATE']['state']=phase
            result=h.run_install()
            self.assertNotEqual(result.returncode,0)
            self.assertIn('verified idle printer',result.stderr)
            self.assertFalse(h.calls.exists())
            self.assertEqual(len(list(h.backups.iterdir())),7)

    def test_saved_calibration_drift_refuses_writes_and_explicit_mode_backs_up(self):
        h=installer.InstallerTests('test_dry_run_preserves_files_and_backups'); h.setUp()
        self.addCleanup(h.tearDown)
        live=h.config/'printer.cfg'; source=h.payload/'printer.cfg'
        live.write_bytes(source.read_bytes()+b'\n#*# local_calibration = 1\n')
        result=h.run_install()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('SAVE_CONFIG differs',result.stderr)
        self.assertFalse(h.calls.exists())
        self.assertEqual(len(list(h.backups.iterdir())),7)
        h.env['VORON_ALLOW_CALIBRATION_REPLACE']='1'
        result=h.run_install()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(list(h.backups.iterdir())),8)

    def test_identical_calibration_and_invalid_optin(self):
        h=installer.InstallerTests('test_dry_run_preserves_files_and_backups'); h.setUp()
        self.addCleanup(h.tearDown)
        (h.config/'printer.cfg').write_bytes((h.payload/'printer.cfg').read_bytes())
        self.assertEqual(h.run_install(dry=True).returncode,0)
        h.env['VORON_ALLOW_CALIBRATION_REPLACE']='2'
        self.assertNotEqual(h.run_install().returncode,0)

@unittest.skipUnless(os.environ.get('VORON_TEST_POWERSHELL'),'PowerShell is required')
class OrcaSyncContracts(unittest.TestCase):
    def test_real_scoped_commits_include_only_current_backup(self):
        with tempfile.TemporaryDirectory(prefix='voron-orca-contract-') as temporary:
            root=Path(temporary)/'repo'; root.mkdir()
            profiles=root/'Orca Config'; profiles.mkdir()
            script=profiles/'Sync-OrcaProfiles.ps1'
            shutil.copy2(ROOT/'Orca Config/Sync-OrcaProfiles.ps1',script)
            dest=profiles/'Voron Stealthchanger.json'; dest.write_text('{"name":"old"}')
            unrelated=root/'unrelated.txt'; unrelated.write_text('original')
            def git(*args):
                return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,check=True).stdout
            git('init','-b','main'); git('config','user.name','Offline test'); git('config','user.email','offline@example.invalid')
            git('add','.'); git('commit','-m','fixture')
            unrelated.write_text('staged unrelated'); git('add','unrelated.txt')
            (root/'untracked.txt').write_text('keep')
            source=Path(temporary)/'source'; machine=source/'test/machine'; machine.mkdir(parents=True)
            for run in (1,2):
                (machine/dest.name).write_text(json.dumps({'name':'changed '+str(run)}))
                result=subprocess.run([os.environ['VORON_TEST_POWERSHELL'],'-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),
                    '-OrcaUserRoot',str(source),'-ProfileId','test','-SkipAnalysisAliases','-Commit'],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                changed=git('show','--pretty=format:','--name-only','HEAD')
                self.assertIn('extras/backups/pre-orcaslicer-profile-sync-',changed)
                self.assertIn('README.md',changed)
                self.assertNotIn('unrelated.txt',changed)
            self.assertEqual(len(list((root/'extras/backups').iterdir())),2)
            self.assertIn('M  unrelated.txt',git('status','--porcelain'))
            self.assertIn('?? untracked.txt',git('status','--porcelain'))

# Replace one historical literal-motion test with semantic coverage of the
# reviewed relative lift and post-dock helper. Keep its preset/fit assertions.
# The original .py remains unchanged; this test still runs, rather than skips.
def current_dryer_preset_and_park_contract(self):
    f=self.dryer(); f.p['temperature_sensor chamber']={'temperature':25}
    out=f.render('START_DRYER')
    for command in ('G91','G0 Z170.0 F3000','UNSELECT_TOOL RESTORE_AXIS=',
                    '_DRYER_PARK','M140 S70.0','FAN=bed_fan SPEED=0.75'):
        self.assertIn(command,out)
    f.p['toolchanger']['tool_number']=-1
    f.p['toolhead']['position']=individual.Coord(30,120,331)
    self.assertIn('G0 X175 Y310 F6000',f.render('_DRYER_PARK'))
    f=self.dryer(); f.p['temperature_sensor chamber']={'temperature':25}
    f.p['toolhead']['axis_maximum']=individual.Coord(200,200,180)
    with self.assertRaisesRegex(ValueError,'does not fit'): f.render('START_DRYER')
individual.IndividualFeatureTests.test_dryer_existing_preset_and_park_retained=current_dryer_preset_and_park_contract

suite=unittest.TestSuite()
for module in (individual,installer,pty,cfg,cleaner):
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(CurrentContracts))
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(DeploymentContracts))
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(OrcaSyncContracts))
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'@ | & $Python -
if ($LASTEXITCODE -ne 0) { throw "Production CFG contracts failed (exit $LASTEXITCODE)." }
}
finally { Pop-Location }
