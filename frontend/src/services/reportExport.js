import JSZip from 'jszip'
import jsPDF from 'jspdf'
import api from './api'

class ReportExportService {
  constructor() {
    this.zip = new JSZip()
  }

  // Générer le rapport PDF principal
  async generateMainReport(analysisData, selectedBuildings, startYear, startMonth, endYear, endMonth) {
    const doc = new jsPDF()
    
    // Titre
    doc.setFontSize(20)
    doc.text('Rapport d\'Analyse de Rentabilité', 20, 30)
    
    // Période
    doc.setFontSize(12)
    const periodText = `Période: ${startMonth}/${startYear} à ${endMonth}/${endYear}`
    doc.text(periodText, 20, 45)
    
    // Métriques clés
    doc.setFontSize(14)
    doc.text('Métriques Clés', 20, 65)
    
    doc.setFontSize(10)
    const summary = analysisData.summary
    doc.text(`Revenus totaux: $${summary.totalRevenue.toLocaleString()}`, 20, 80)
    doc.text(`Dépenses totales: $${summary.totalExpenses.toLocaleString()}`, 20, 90)
    doc.text(`Cashflow net: $${summary.netCashflow.toLocaleString()}`, 20, 100)
    
    // Détail par immeuble
    doc.setFontSize(14)
    doc.text('Détail par Immeuble', 20, 120)
    
    doc.setFontSize(10)
    let yPos = 135
    analysisData.buildings.forEach((building, index) => {
      if (yPos > 280) {
        doc.addPage()
        yPos = 20
      }
      
      doc.text(`${building.name}:`, 20, yPos)
      doc.text(`  Revenus: $${building.summary.totalRevenue.toLocaleString()}`, 30, yPos + 5)
      doc.text(`  Dépenses: $${building.summary.totalExpenses.toLocaleString()}`, 30, yPos + 10)
      doc.text(`  Cashflow: $${building.summary.netCashflow.toLocaleString()}`, 30, yPos + 15)
      
      yPos += 25
    })
    
    // Données mensuelles
    doc.setFontSize(14)
    doc.text('Évolution Mensuelle', 20, yPos + 10)
    
    doc.setFontSize(10)
    yPos += 25
    analysisData.monthlyTotals.forEach((month, index) => {
      if (yPos > 280) {
        doc.addPage()
        yPos = 20
      }
      
      doc.text(`${month.month}: Revenus $${month.revenue.toLocaleString()}, Dépenses $${month.expenses.toLocaleString()}, Cashflow $${month.netCashflow.toLocaleString()}`, 20, yPos)
      yPos += 10
    })
    
    return doc.output('blob')
  }

  // Organiser les PDFs par mois/type/catégorie
  async organizeTransactionPDFs(analysisData, startYear, startMonth, endYear, endMonth) {
    const documentsFolder = this.zip.folder('Documents')
    
    // Créer la structure de dossiers pour chaque mois
    const currentDate = new Date(startYear, startMonth - 1, 1)
    const endDate = new Date(endYear, endMonth - 1, 1)
    
    while (currentDate <= endDate) {
      const yearMonth = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`
      const monthFolder = documentsFolder.folder(yearMonth)
      
      // Créer les dossiers Revenus et Dépenses
      const revenusFolder = monthFolder.folder('Revenus')
      const depensesFolder = monthFolder.folder('Depenses')
      
      // Créer les sous-dossiers pour les catégories
      const revenusCategories = ['Capital', 'Loyers']
      const depensesCategories = [
        'Assurances', 'Frais d\'utilisation', 'Frais fixes d\'utilisation',
        'Frais dépôt commercial', 'Hydro Québec', 'Frais crédit',
        'Intérêts', 'Frais de gestion', 'Taxes scolaires', 'Taxes municipales',
        'Entretien', 'Réparation mineure', 'Réparation majeure',
        'Internet', 'Fournitures'
      ]
      
      revenusCategories.forEach(cat => revenusFolder.folder(cat))
      depensesCategories.forEach(cat => depensesFolder.folder(cat))
      
      // Passer au mois suivant
      currentDate.setMonth(currentDate.getMonth() + 1)
    }
    
    // Récupérer et organiser les PDFs des transactions
    await this.fetchAndOrganizeTransactionPDFs(documentsFolder, startYear, startMonth, endYear, endMonth)
    
    // Récupérer et organiser les PDFs des baux (loyers)
    await this.fetchAndOrganizeLeasePDFs(documentsFolder, startYear, startMonth, endYear, endMonth)
  }

  // Récupérer les PDFs des transactions
  async fetchAndOrganizeTransactionPDFs(documentsFolder, startYear, startMonth, endYear, endMonth) {
    try {
      // Récupérer toutes les transactions pour la période
      const response = await api.get('/api/transactions')
      const transactions = response.data.data || response.data
      
      const startDate = new Date(startYear, startMonth - 1, 1)
      const endDate = new Date(endYear, endMonth, 0) // Dernier jour du mois de fin
      
      for (const transaction of transactions) {
        if (transaction.pdf_transaction && transaction.date_de_transaction) {
          const transactionDate = new Date(transaction.date_de_transaction)
          
          // Vérifier si la transaction est dans la période
          if (transactionDate >= startDate && transactionDate <= endDate) {
            const yearMonth = `${transactionDate.getFullYear()}-${String(transactionDate.getMonth() + 1).padStart(2, '0')}`
            const typeFolder = transaction.type === 'revenu' ? 'Revenus' : 'Depenses'
            const categoryFolder = transaction.categorie || 'Autres'
            
            try {
              // Télécharger le PDF depuis Backblaze B2
              const pdfResponse = await fetch(`/api/documents/${transaction.pdf_transaction}`)
              if (pdfResponse.ok) {
                const pdfBlob = await pdfResponse.blob()
                
                // Ajouter le PDF au ZIP dans le bon dossier
                const folderPath = `${yearMonth}/${typeFolder}/${categoryFolder}`
                documentsFolder.folder(folderPath).file(transaction.pdf_transaction, pdfBlob)
              }
            } catch (error) {
              console.warn(`Impossible de récupérer le PDF ${transaction.pdf_transaction}:`, error)
            }
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des transactions:', error)
    }
  }

  // Récupérer les PDFs des baux (loyers)
  async fetchAndOrganizeLeasePDFs(documentsFolder, startYear, startMonth, endYear, endMonth) {
    try {
      // Récupérer tous les baux
      const response = await api.get('/api/leases')
      const leases = response.data.data || response.data
      
      const startDate = new Date(startYear, startMonth - 1, 1)
      const endDate = new Date(endYear, endMonth, 0)
      
      for (const lease of leases) {
        if (lease.pdf_bail && lease.date_debut && lease.date_fin) {
          const leaseStart = new Date(lease.date_debut)
          const leaseEnd = new Date(lease.date_fin)
          
          // Vérifier si le bail chevauche avec la période
          if (leaseStart <= endDate && leaseEnd >= startDate) {
            // Pour les loyers, on les met dans chaque mois actif du bail
            const currentDate = new Date(Math.max(leaseStart, startDate))
            const finalEndDate = new Date(Math.min(leaseEnd, endDate))
            
            while (currentDate <= finalEndDate) {
              const yearMonth = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`
              
              try {
                // Télécharger le PDF depuis Backblaze B2
                const pdfResponse = await fetch(`/api/documents/${lease.pdf_bail}`)
                if (pdfResponse.ok) {
                  const pdfBlob = await pdfResponse.blob()
                  
                  // Ajouter le PDF au ZIP dans le dossier Loyers
                  const folderPath = `${yearMonth}/Revenus/Loyers`
                  documentsFolder.folder(folderPath).file(lease.pdf_bail, pdfBlob)
                }
              } catch (error) {
                console.warn(`Impossible de récupérer le PDF ${lease.pdf_bail}:`, error)
              }
              
              // Passer au mois suivant
              currentDate.setMonth(currentDate.getMonth() + 1)
            }
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des baux:', error)
    }
  }

  // Générer et télécharger le rapport complet
  async exportReport(analysisData, selectedBuildings, startYear, startMonth, endYear, endMonth) {
    try {
      // Générer le rapport PDF principal
      const mainReportBlob = await this.generateMainReport(analysisData, selectedBuildings, startYear, startMonth, endYear, endMonth)
      this.zip.file('Rapport_Principal.pdf', mainReportBlob)
      
      // Organiser les PDFs des transactions et baux
      await this.organizeTransactionPDFs(analysisData, startYear, startMonth, endYear, endMonth)
      
      // Générer et télécharger le ZIP
      const zipBlob = await this.zip.generateAsync({ type: 'blob' })
      
      // Créer le nom du fichier avec la période
      const fileName = `Rapport_Rentabilite_${startYear}-${String(startMonth).padStart(2, '0')}_${endYear}-${String(endMonth).padStart(2, '0')}.zip`
      
      // Télécharger le fichier
      const url = window.URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      console.error('Erreur lors de l\'export du rapport:', error)
      throw error
    }
  }
}

export default new ReportExportService()
