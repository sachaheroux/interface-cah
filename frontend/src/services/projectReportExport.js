import JSZip from 'jszip'
import { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, HeadingLevel } from 'docx'
import api from './api'

class ProjectReportExportService {
  constructor() {
    this.zip = new JSZip()
  }

  // Générer le rapport Word principal
  async generateMainReport(analysisData, project) {
    const sections = []

    // Titre
    sections.push(
      new Paragraph({
        text: `Rapport d'Analyse de Projet`,
        heading: HeadingLevel.TITLE,
        spacing: { after: 400 }
      })
    )

    // Informations du projet
    sections.push(
      new Paragraph({
        text: `Projet: ${project.nom || 'N/A'}`,
        spacing: { after: 200 }
      })
    )

    if (project.budget_total) {
      sections.push(
        new Paragraph({
          text: `Budget total: ${this.formatCurrency(project.budget_total)}`,
          spacing: { after: 200 }
        })
      )
    }

    // Totaux généraux
    sections.push(
      new Paragraph({
        text: 'Résumé des Dépenses',
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 400, after: 200 }
      })
    )

    const totalsTable = new Table({
      rows: [
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph('Type')],
              width: { size: 50, type: WidthType.PERCENTAGE }
            }),
            new TableCell({
              children: [new Paragraph('Montant')],
              width: { size: 50, type: WidthType.PERCENTAGE }
            })
          ]
        }),
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph('Sous-traitants')]
            }),
            new TableCell({
              children: [new Paragraph(this.formatCurrency(analysisData.totaux.sous_traitants))]
            })
          ]
        }),
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph('Commandes')]
            }),
            new TableCell({
              children: [new Paragraph(this.formatCurrency(analysisData.totaux.commandes))]
            })
          ]
        }),
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph('Employés')]
            }),
            new TableCell({
              children: [new Paragraph(this.formatCurrency(analysisData.totaux.employes))]
            })
          ]
        }),
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph({ text: 'Total', bold: true })]
            }),
            new TableCell({
              children: [new Paragraph({ text: this.formatCurrency(analysisData.totaux.total), bold: true })]
            })
          ]
        })
      ],
      width: { size: 100, type: WidthType.PERCENTAGE }
    })

    sections.push(totalsTable)

    // Dépenses par catégorie
    sections.push(
      new Paragraph({
        text: 'Dépenses par Catégorie',
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 400, after: 200 }
      })
    )

    const categoryTable = new Table({
      rows: [
        new TableRow({
          children: [
            new TableCell({
              children: [new Paragraph('Catégorie')],
              width: { size: 30, type: WidthType.PERCENTAGE }
            }),
            new TableCell({
              children: [new Paragraph('Sous-traitants')],
              width: { size: 20, type: WidthType.PERCENTAGE }
            }),
            new TableCell({
              children: [new Paragraph('Commandes')],
              width: { size: 20, type: WidthType.PERCENTAGE }
            }),
            new TableCell({
              children: [new Paragraph('Employés')],
              width: { size: 15, type: WidthType.PERCENTAGE }
            }),
            new TableCell({
              children: [new Paragraph('Total')],
              width: { size: 15, type: WidthType.PERCENTAGE }
            })
          ]
        }),
        ...analysisData.depenses_par_section.map(item =>
          new TableRow({
            children: [
              new TableCell({
                children: [new Paragraph(item.section || 'Non spécifié')]
              }),
              new TableCell({
                children: [new Paragraph(this.formatCurrency(item.sous_traitants))]
              }),
              new TableCell({
                children: [new Paragraph(this.formatCurrency(item.commandes))]
              }),
              new TableCell({
                children: [new Paragraph(this.formatCurrency(item.employes))]
              }),
              new TableCell({
                children: [new Paragraph({ text: this.formatCurrency(item.total), bold: true })]
              })
            ]
          })
        )
      ],
      width: { size: 100, type: WidthType.PERCENTAGE }
    })

    sections.push(categoryTable)

    // Comparaison avec le budget
    if (project.budget_total) {
      const total = analysisData.totaux.total
      const budget = project.budget_total
      const percentage = budget > 0 ? (total / budget) * 100 : 0
      const remaining = budget - total

      sections.push(
        new Paragraph({
          text: 'Comparaison avec le Budget',
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 400, after: 200 }
        })
      )

      sections.push(
        new Paragraph({
          children: [
            new TextRun({ text: `Budget total: `, bold: true }),
            new TextRun(this.formatCurrency(budget))
          ],
          spacing: { after: 100 }
        })
      )

      sections.push(
        new Paragraph({
          children: [
            new TextRun({ text: `Dépenses totales: `, bold: true }),
            new TextRun(this.formatCurrency(total))
          ],
          spacing: { after: 100 }
        })
      )

      sections.push(
        new Paragraph({
          children: [
            new TextRun({ text: percentage > 100 ? `Dépassement: ` : `Reste disponible: `, bold: true }),
            new TextRun({
              text: this.formatCurrency(Math.abs(remaining)),
              color: percentage > 100 ? 'FF0000' : '000000'
            })
          ],
          spacing: { after: 100 }
        })
      )

      sections.push(
        new Paragraph({
          children: [
            new TextRun({ text: `Pourcentage utilisé: `, bold: true }),
            new TextRun({
              text: `${percentage.toFixed(1)}%`,
              color: percentage > 100 ? 'FF0000' : percentage > 80 ? 'FFA500' : '000000'
            })
          ],
          spacing: { after: 200 }
        })
      )
    }

    const doc = new Document({
      sections: [{ children: sections }]
    })

    const blob = await Packer.toBlob(doc)
    return blob
  }

  // Organiser les PDFs par type et catégorie
  async organizePDFs(projectId, analysisData) {
    const documentsFolder = this.zip.folder('Documents')

    // Dossiers par type
    const sousTraitantsFolder = documentsFolder.folder('Sous-traitants')
    const fournisseursFolder = documentsFolder.folder('Fournisseurs')
    const employesFolder = documentsFolder.folder('Employes')

    // Organiser les factures ST (sous-traitants)
    await this.organizeFacturesST(sousTraitantsFolder, projectId, analysisData)

    // Organiser les commandes (fournisseurs)
    await this.organizeCommandes(fournisseursFolder, projectId, analysisData)

    // Créer les documents Word pour les employés
    await this.organizeEmployes(employesFolder, projectId, analysisData)
  }

  // Organiser les factures ST par catégorie
  async organizeFacturesST(folder, projectId, analysisData) {
    try {
      const response = await api.get(`/api/construction/factures-st`)
      const factures = response.data.data || response.data || []

      // Filtrer les factures du projet
      const projectFactures = factures.filter(f => f.id_projet === projectId)

      // Grouper par catégorie
      const facturesByCategory = {}
      projectFactures.forEach(facture => {
        const category = facture.section || 'Non spécifié'
        if (!facturesByCategory[category]) {
          facturesByCategory[category] = []
        }
        facturesByCategory[category].push(facture)
      })

      // Créer un dossier par catégorie et y mettre les PDFs
      for (const [category, facturesList] of Object.entries(facturesByCategory)) {
        const categoryFolder = folder.folder(category)
        
        for (const facture of facturesList) {
          if (facture.pdf_facture) {
            try {
              const pdfResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${facture.pdf_facture}`)
              if (pdfResponse.ok) {
                const pdfBlob = await pdfResponse.blob()
                const filename = facture.pdf_facture.split('/').pop() || facture.pdf_facture
                categoryFolder.file(filename, pdfBlob)
              }
            } catch (error) {
              console.warn(`Impossible de récupérer le PDF ${facture.pdf_facture}:`, error)
            }
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des factures ST:', error)
    }
  }

  // Organiser les commandes par catégorie
  async organizeCommandes(folder, projectId, analysisData) {
    try {
      const response = await api.get(`/api/construction/commandes`)
      const commandes = response.data.data || response.data || []

      // Filtrer les commandes du projet
      const projectCommandes = commandes.filter(c => c.id_projet === projectId)

      // Grouper par catégorie (via les lignes de commande)
      const commandesByCategory = {}
      projectCommandes.forEach(commande => {
        if (commande.lignes_commande && commande.lignes_commande.length > 0) {
          commande.lignes_commande.forEach(ligne => {
            const category = ligne.section || 'Non spécifié'
            if (!commandesByCategory[category]) {
              commandesByCategory[category] = []
            }
            // Ajouter la commande si elle n'est pas déjà dans la liste
            if (!commandesByCategory[category].some(c => c.id_commande === commande.id_commande)) {
              commandesByCategory[category].push(commande)
            }
          })
        }
      })

      // Créer un dossier par catégorie et y mettre les PDFs
      for (const [category, commandesList] of Object.entries(commandesByCategory)) {
        const categoryFolder = folder.folder(category)
        
        for (const commande of commandesList) {
          if (commande.pdf_commande) {
            try {
              const pdfResponse = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${commande.pdf_commande}`)
              if (pdfResponse.ok) {
                const pdfBlob = await pdfResponse.blob()
                const filename = commande.pdf_commande.split('/').pop() || commande.pdf_commande
                categoryFolder.file(filename, pdfBlob)
              }
            } catch (error) {
              console.warn(`Impossible de récupérer le PDF ${commande.pdf_commande}:`, error)
            }
          }
        }
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des commandes:', error)
    }
  }

  // Organiser les employés par catégorie avec documents Word
  async organizeEmployes(folder, projectId, analysisData) {
    try {
      const response = await api.get(`/api/construction/punchs-employes`)
      const punchs = response.data.data || response.data || []

      // Filtrer les punchs du projet
      const projectPunchs = punchs.filter(p => p.id_projet === projectId)

      // Grouper par catégorie et par employé
      const punchsByCategory = {}
      projectPunchs.forEach(punch => {
        const category = punch.section || 'Non spécifié'
        if (!punchsByCategory[category]) {
          punchsByCategory[category] = {}
        }
        const employeeName = punch.employe 
          ? `${punch.employe.prenom || ''} ${punch.employe.nom || ''}`.trim()
          : 'Employé inconnu'
        if (!punchsByCategory[category][employeeName]) {
          punchsByCategory[category][employeeName] = {
            totalHours: 0,
            punchs: []
          }
        }
        punchsByCategory[category][employeeName].totalHours += punch.heure_travaillee || 0
        punchsByCategory[category][employeeName].punchs.push(punch)
      })

      // Créer un document Word par catégorie
      for (const [category, employees] of Object.entries(punchsByCategory)) {
        const sections = []

        // Titre
        sections.push(
          new Paragraph({
            text: `Heures travaillées - ${category}`,
            heading: HeadingLevel.TITLE,
            spacing: { after: 400 }
          })
        )

        // Tableau des heures par employé
        const tableRows = [
          new TableRow({
            children: [
              new TableCell({
                children: [new Paragraph('Employé')],
                width: { size: 50, type: WidthType.PERCENTAGE }
              }),
              new TableCell({
                children: [new Paragraph('Heures travaillées')],
                width: { size: 50, type: WidthType.PERCENTAGE }
              })
            ]
          })
        ]

        let totalCategoryHours = 0
        for (const [employeeName, data] of Object.entries(employees)) {
          totalCategoryHours += data.totalHours
          tableRows.push(
            new TableRow({
              children: [
                new TableCell({
                  children: [new Paragraph(employeeName)]
                }),
                new TableCell({
                  children: [new Paragraph(`${data.totalHours.toFixed(2)} h`)]
                })
              ]
            })
          )
        }

        // Ligne total
        tableRows.push(
          new TableRow({
            children: [
              new TableCell({
                children: [new Paragraph({ text: 'Total', bold: true })]
              }),
              new TableCell({
                children: [new Paragraph({ text: `${totalCategoryHours.toFixed(2)} h`, bold: true })]
              })
            ]
          })
        )

        const table = new Table({
          rows: tableRows,
          width: { size: 100, type: WidthType.PERCENTAGE }
        })

        sections.push(table)

        const doc = new Document({
          sections: [{ children: sections }]
        })

        const blob = await Packer.toBlob(doc)
        const safeCategoryName = category.replace(/[^a-zA-Z0-9]/g, '_')
        folder.file(`${safeCategoryName}_Heures_Travaillees.docx`, blob)
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des punchs:', error)
    }
  }

  // Générer et télécharger le rapport complet
  async exportReport(analysisData, project) {
    try {
      // Réinitialiser le ZIP
      this.zip = new JSZip()

      // Générer le rapport Word principal
      const mainReportBlob = await this.generateMainReport(analysisData, project)
      const safeProjectName = (project.nom || 'Projet').replace(/[^a-zA-Z0-9]/g, '_')
      this.zip.file(`Rapport_Principal_${safeProjectName}.docx`, mainReportBlob)

      // Organiser les PDFs par type et catégorie
      await this.organizePDFs(project.id_projet, analysisData)

      // Générer et télécharger le ZIP
      const zipBlob = await this.zip.generateAsync({ type: 'blob' })

      // Créer le nom du fichier
      const fileName = `Rapport_Projet_${safeProjectName}_${new Date().toISOString().split('T')[0]}.zip`

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

  formatCurrency(amount) {
    if (!amount || amount === 0) return '$0.00'
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }
}

export default new ProjectReportExportService()

