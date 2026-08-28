import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../store/shelterStore';
import { checkPolicyCompliance } from '../api/endpoints';
import {
  FileCheck2,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Building2,
  CheckCircle2,
  BookOpen,
  ArrowRight,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';

export const PolicyCompliancePage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentDesign,
    selectedState,
    setSelectedState,
    complianceResult,
    setComplianceResult,
    isLoadingCompliance,
    setIsLoadingCompliance,
    simulationResult
  } = useShelterStore();

  const indianStates = [
    'Odisha',
    'Rajasthan',
    'Maharashtra',
    'Gujarat',
    'Karnataka',
    'Tamil Nadu',
    'West Bengal',
    'Uttar Pradesh',
    'Bihar',
    'Madhya Pradesh',
    'Kerala',
    'Assam',
    'Punjab',
    'Haryana',
    'Telangana',
    'Delhi'
  ];

  const runAudit = async () => {
    setIsLoadingCompliance(true);
    try {
      const simMetrics = simulationResult?.summary ? {
        u_wall: simulationResult.u_wall,
        u_roof: simulationResult.u_roof,
        comfort_score: simulationResult.summary.comfort_score,
        peak_indoor_temp: simulationResult.summary.peak_indoor_temp_c
      } : undefined;

      const data = await checkPolicyCompliance({
        state_name: selectedState,
        building_type: currentDesign.archetype || 'Residential / Transitional Shelter',
        geometry: currentDesign.geometry,
        materials: currentDesign.materials,
        simulation_metrics: simMetrics
      });
      setComplianceResult(data);
    } catch (err) {
      console.error('Failed to run compliance audit:', err);
    } finally {
      setIsLoadingCompliance(false);
    }
  };

  useEffect(() => {
    runAudit();
  }, [selectedState, currentDesign]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PASS':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>✓ PASS</span>
          </span>
        );
      case 'REVIEW':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>⚠ REVIEW</span>
          </span>
        );
      case 'FAIL':
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3.5 h-3.5" />
            <span>✕ FAIL</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-slate-500/10 text-slate-400 border border-slate-500/30">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>? NOT VERIFIED</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md text-[10px] font-mono uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Module 10 — Policy & Compliance
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-2 flex items-center gap-3">
            State-Specific Building Policy & Compliance Checker
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Automated screening against Eco-Niwas Samhita (ENS 2021), ECBC, NBC 2016, and State Energy Conservation & Development Control Byelaws.
          </p>
        </div>

        {/* State Selector */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2 bg-surface p-1.5 rounded-xl border border-surface-border">
            <span className="text-xs text-slate-400 px-2 font-mono">Jurisdiction:</span>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="bg-surface-raised border border-surface-border rounded-lg text-xs font-semibold text-white px-3 py-1.5 focus:outline-none focus:border-emerald-500"
            >
              {indianStates.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={runAudit}
            disabled={isLoadingCompliance}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg shadow-emerald-950/40 transition disabled:opacity-50"
          >
            <RefreshCw className={clsx('w-3.5 h-3.5', isLoadingCompliance && 'animate-spin')} />
            <span>Re-Audit Design</span>
          </button>
        </div>
      </div>

      {/* Compliance Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-surface/80 border border-amber-500/30 flex items-start gap-3.5 text-xs text-slate-300">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <p className="font-semibold text-emerald-300">Preliminary Regulatory Screening Notice</p>
          <p className="text-slate-400 leading-relaxed">
            ShelterAI provides preliminary design and energy compliance screening based on published central codes and state building byelaws. <strong>It is not a substitute for formal approval by the competent municipal authority or structural certification by licensed professionals.</strong>
          </p>
        </div>
      </div>

      {/* Summary Scorecard */}
      {complianceResult && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <div className="p-4 rounded-2xl bg-surface border border-surface-border space-y-1">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Overall Audit</div>
            <div className="pt-1">{getStatusBadge(complianceResult.overall_status)}</div>
          </div>
          <div className="p-4 rounded-2xl bg-surface border border-surface-border space-y-1">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Pass Count</div>
            <div className="text-2xl font-mono font-bold text-emerald-400">{complianceResult.summary.pass}</div>
          </div>
          <div className="p-4 rounded-2xl bg-surface border border-surface-border space-y-1">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Review Needed</div>
            <div className="text-2xl font-mono font-bold text-amber-400">{complianceResult.summary.review}</div>
          </div>
          <div className="p-4 rounded-2xl bg-surface border border-surface-border space-y-1">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Fail Count</div>
            <div className="text-2xl font-mono font-bold text-rose-400">{complianceResult.summary.fail}</div>
          </div>
          <div className="p-4 rounded-2xl bg-surface border border-surface-border space-y-1">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Not Verified</div>
            <div className="text-2xl font-mono font-bold text-slate-400">{complianceResult.summary.not_verified}</div>
          </div>
        </div>
      )}

      {/* Compliance Rule Results Table / Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-emerald-400" />
            <span>Audited Building Standards & Byelaw Clauses</span>
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            Active Jurisdiction: {selectedState} (State + National)
          </span>
        </div>

        {isLoadingCompliance ? (
          <div className="p-16 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-8 h-8 mx-auto animate-spin text-emerald-400" />
            <p>Auditing geometry, envelope U-values, opening ratios, and state adaptations...</p>
          </div>
        ) : (
          <div className="space-y-3">
            {complianceResult?.results.map((rule) => (
              <div
                key={rule.id}
                className="p-5 rounded-2xl bg-surface border border-surface-border flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-slate-800 text-slate-300 border border-slate-700">
                      {rule.jurisdiction}
                    </span>
                    <span className="text-xs font-mono text-emerald-400">{rule.category}</span>
                    <span className="text-[11px] text-slate-400">({rule.clause})</span>
                  </div>

                  <p className="text-sm font-semibold text-white">{rule.requirement}</p>
                  <p className="text-xs text-slate-400">{rule.reason}</p>

                  {rule.status !== 'PASS' && rule.remediation && (
                    <div className="p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300/90">
                      <strong>Remediation:</strong> {rule.remediation}
                    </div>
                  )}

                  <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono pt-1">
                    <span>Source: {rule.source}</span>
                    <span>Verified: {rule.last_verified}</span>
                  </div>
                </div>

                <div className="flex md:flex-col items-end justify-between md:justify-center gap-2 shrink-0">
                  {getStatusBadge(rule.status)}
                  <div className="text-[11px] font-mono text-slate-400">
                    Threshold: {rule.required_threshold}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
