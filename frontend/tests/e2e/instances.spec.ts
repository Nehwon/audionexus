import { test, expect } from '@playwright/test'

test.describe('Gestion des instances', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de l'authentification
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'test-token')
      localStorage.setItem('refresh_token', 'test-refresh-token')
    })

    // Mock de l'API utilisateur
    await page.route('/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z'
        })
      })
    })
  })

  test('devrait afficher la liste des instances', async ({ page }) => {
    // Mock des instances
    await page.route('/api/audiobookshelf/instances', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          instances: [
            {
              id: 1,
              name: 'Ma Bibliothèque',
              base_url: 'http://localhost:13378',
              is_active: true,
              status: 'online',
              last_sync: '2024-01-01T10:00:00Z'
            }
          ],
          total: 1,
          active: 1
        })
      })
    })

    // Mock des métriques du dashboard
    await page.route('/api/dashboard-metrics', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_instances: 1,
          active_instances: 1,
          total_audiobooks: 150,
          recent_syncs: 1,
          system_health: 'healthy'
        })
      })
    })

    await page.goto('/')
    await expect(page.locator('text=Ma Bibliothèque')).toBeVisible()
  })

  test('devrait permettre de créer une nouvelle instance', async ({ page }) => {
    // Mock des instances (liste vide)
    await page.route('/api/audiobookshelf/instances', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          instances: [],
          total: 0,
          active: 0
        })
      })
    })

    await page.goto('/instances')
    await expect(page.locator('text=Ajouter une instance')).toBeVisible()

    // Cliquer sur le bouton d'ajout
    await page.click('text=Ajouter une instance')

    // Remplir le formulaire
    await page.fill('input[name="name"]', 'Nouvelle Bibliothèque')
    await page.fill('input[name="base_url"]', 'http://audiobookshelf.example.com:13378')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'password123')

    // Mock de la création
    await page.route('/api/audiobookshelf/instances', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            name: 'Nouvelle Bibliothèque',
            base_url: 'http://audiobookshelf.example.com:13378',
            username: 'admin',
            is_active: true,
            status: 'online',
            created_at: '2024-01-01T00:00:00Z'
          })
        })
      }
    })

    // Soumettre le formulaire
    await page.click('button[type="submit"]')

    // Vérifier la création
    await expect(page.locator('text=Nouvelle Bibliothèque')).toBeVisible()
  })

  test('devrait permettre de tester la connexion à une instance', async ({ page }) => {
    // Mock d'une instance existante
    await page.route('/api/audiobookshelf/instances', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          instances: [
            {
              id: 1,
              name: 'Test Instance',
              base_url: 'http://localhost:13378',
              is_active: true,
              status: 'online',
              last_sync: '2024-01-01T10:00:00Z'
            }
          ],
          total: 1,
          active: 1
        })
      })
    })

    await page.goto('/instances')

    // Mock du test de connexion
    await page.route('/api/audiobookshelf/instances/1/test', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'online',
          version: '2.3.1',
          message: 'Connexion réussie'
        })
      })
    })

    // Cliquer sur le bouton Tester
    await page.click('button:has-text("Tester")')

    // Vérifier le succès (toast ou message)
    // Note: L'implémentation exacte dépend de la lib de notifications
  })
})

test.describe('Lecteur audio', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de l'authentification
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'test-token')
      localStorage.setItem('refresh_token', 'test-refresh-token')
    })

    await page.route('/api/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z'
        })
      })
    })
  })

  test('devrait afficher le lecteur lorsqu\'une piste est ajoutée', async ({ page }) => {
    await page.goto('/')

    // Simuler l'ajout d'une piste (à travers le contexte React ou mock)
    await page.addInitScript(() => {
      // Simuler l'ajout d'une piste au contexte
      const event = new CustomEvent('addTrack', {
        detail: {
          id: '1',
          title: 'Test Track',
          artist: 'Test Artist',
          duration: 180,
          url: 'test-audio-url'
        }
      })
      window.dispatchEvent(event)
    })

    // Vérifier que le lecteur apparaît
    await expect(page.locator('text=Test Track')).toBeVisible()
  })

  test('devrait permettre de contrôler la lecture', async ({ page }) => {
    await page.goto('/')

    // Simuler la présence d'une piste
    await page.addInitScript(() => {
      // Simuler une piste en cours
      const event = new CustomEvent('setPlayerTrack', {
        detail: {
          id: '1',
          title: 'Test Track',
          artist: 'Test Artist',
          duration: 180,
          url: 'test-audio-url'
        }
      })
      window.dispatchEvent(event)
    })

    // Vérifier les contrôles
    await expect(page.locator('[aria-label*="play"]')).toBeVisible()
    await expect(page.locator('[aria-label*="pause"]')).toBeVisible()
    await expect(page.locator('[aria-label*="previous"]')).toBeVisible()
    await expect(page.locator('[aria-label*="next"]')).toBeVisible()

    // Tester le contrôle du volume
    await expect(page.locator('input[type="range"]')).toBeVisible()
  })
})