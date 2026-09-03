import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Toast from './components/Toast';
import RunbookDetailModal from './components/RunbookDetailModal';
import ApprovalModal from './components/ApprovalModal';

import DashboardPage from './pages/DashboardPage';
import IngestionPage from './pages/IngestionPage';
import InvestigationPage from './pages/InvestigationPage';
import AIRecommendationPage from './pages/AIRecommendationPage';
import ApprovalQueuePage from './pages/ApprovalQueuePage';
import RunbooksPage from './pages/RunbooksPage';
import ExperimentPage from './pages/ExperimentPage';

import { api } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [runbooks, setRunbooks] = useState([]);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [toast, setToast] = useState(null);

  // Modals state
  const [selectedRunbook, setSelectedRunbook] = useState(null);
  const [approvalRunbook, setApprovalRunbook] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  // Investigation / AI selection state
  const [investigateIncId, setInvestigateIncId] = useState('INC-052');
  const [investigatePrId, setInvestigatePrId] = useState('PR-142');

  const showToast = (toastObj) => {
    setToast(toastObj);
  };

  const loadInitialData = async () => {
    try {
      const [h, m, rbList] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getMetrics().catch(() => null),
        api.getRunbooks().catch(() => []),
      ]);
      setHealth(h);
      setMetrics(m);
      setRunbooks(rbList || []);
    } catch (err) {
      console.error('Initial data load error:', err);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // One-click demo seed
  const handleSeedDemo = async () => {
    try {
      setLoadingDemo(true);
      const res = await api.seedDemoData(true);
      showToast({
        type: 'success',
        title: 'ERP Knowledge Base Seeded',
        message: `Seeded ${res.counts.incidents} incidents, ${res.counts.events} events across 10 ERP modules.`,
      });
      await loadInitialData();
    } catch (err) {
      showToast({ type: 'error', title: 'Seed Failed', message: err.message });
    } finally {
      setLoadingDemo(false);
    }
  };

  // One-click INC-052 showcase load
  const handleLoadInc052 = async () => {
    try {
      setLoadingDemo(true);
      const rb = await api.loadScenarioInc052();
      setSelectedRunbook(rb);
      showToast({
        type: 'success',
        title: 'Showcase Scenario Loaded',
        message: 'Loaded Incident INC-052 / PR-142: Regional discount before tax (RULE-TAX-104).',
      });
      await loadInitialData();
      setActiveTab('investigation');
      setInvestigateIncId('INC-052');
      setInvestigatePrId('PR-142');
    } catch (err) {
      showToast({ type: 'error', title: 'Load Failed', message: err.message });
    } finally {
      setLoadingDemo(false);
    }
  };

  // Approval handlers
  const handleApprove = async (id, payload) => {
    try {
      setModalLoading(true);
      const updated = await api.approveRunbook(id, payload);
      setApprovalRunbook(null);
      showToast({
        type: 'success',
        title: 'Runbook Approved',
        message: `Runbook ${id} has been verified and approved for production.`,
      });
      await loadInitialData();
    } catch (err) {
      showToast({ type: 'error', title: 'Approval Failed', message: err.message });
    } finally {
      setModalLoading(false);
    }
  };

  const handleReject = async (id, payload) => {
    try {
      setModalLoading(true);
      const updated = await api.rejectRunbook(id, payload);
      setApprovalRunbook(null);
      showToast({
        type: 'info',
        title: 'Runbook Rejected',
        message: `Runbook ${id} rejected. Reason logged in audit history.`,
      });
      await loadInitialData();
    } catch (err) {
      showToast({ type: 'error', title: 'Rejection Failed', message: err.message });
    } finally {
      setModalLoading(false);
    }
  };

  const handleOverride = async (id, payload) => {
    try {
      setModalLoading(true);
      const updated = await api.overrideRunbook(id, payload);
      setApprovalRunbook(null);
      showToast({
        type: 'info',
        title: 'Procedure Overridden',
        message: `Runbook ${id} updated with manual overrides and logged into audit history.`,
      });
      await loadInitialData();
    } catch (err) {
      showToast({ type: 'error', title: 'Override Failed', message: err.message });
    } finally {
      setModalLoading(false);
    }
  };

  const handleNavigateToAi = (incId, prId) => {
    setInvestigateIncId(incId);
    setInvestigatePrId(prId);
    setActiveTab('ai-recommend');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-[#FFF5F7] via-[#FAF5FF] to-[#FDF2F8]">
      
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        onSeedDemo={handleSeedDemo}
        onLoadInc052={handleLoadInc052}
        loadingDemo={loadingDemo}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && (
          <DashboardPage
            metrics={metrics}
            runbooks={runbooks}
            onSelectRunbook={setSelectedRunbook}
            onNavigateTab={setActiveTab}
            onLoadInc052={handleLoadInc052}
          />
        )}

        {activeTab === 'ingestion' && (
          <IngestionPage onShowToast={showToast} />
        )}

        {activeTab === 'investigation' && (
          <InvestigationPage
            onShowToast={showToast}
            onNavigateToAi={handleNavigateToAi}
          />
        )}

        {activeTab === 'ai-recommend' && (
          <AIRecommendationPage
            selectedIncidentId={investigateIncId}
            selectedPrId={investigatePrId}
            onShowToast={showToast}
            onOpenApproval={setApprovalRunbook}
            onViewRunbook={setSelectedRunbook}
          />
        )}

        {activeTab === 'approvals' && (
          <ApprovalQueuePage
            onOpenApproval={setApprovalRunbook}
            onShowToast={showToast}
          />
        )}

        {activeTab === 'runbooks' && (
          <RunbooksPage
            onSelectRunbook={setSelectedRunbook}
            onShowToast={showToast}
          />
        )}

        {activeTab === 'experiment' && (
          <ExperimentPage
            metrics={metrics}
            onShowToast={showToast}
          />
        )}
      </main>

      {/* Modals & Toasts */}
      <RunbookDetailModal
        isOpen={Boolean(selectedRunbook)}
        onClose={() => setSelectedRunbook(null)}
        runbook={selectedRunbook}
        onOpenApproval={setApprovalRunbook}
      />

      <ApprovalModal
        isOpen={Boolean(approvalRunbook)}
        onClose={() => setApprovalRunbook(null)}
        runbook={approvalRunbook}
        onApprove={handleApprove}
        onReject={handleReject}
        onOverride={handleOverride}
        loading={modalLoading}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />

      {/* Footer */}
      <footer className="border-t border-pink-100/80 bg-white/60 backdrop-blur-sm py-4 text-center text-xs text-slate-400">
        <p>
          Fix2Runbook Prototype • Evidence-Driven ERP Maintenance Knowledge Capture Assistant • Hybrid Event & Rule Architecture
        </p>
      </footer>

    </div>
  );
}
