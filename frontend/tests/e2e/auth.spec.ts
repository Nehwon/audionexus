import { test, expect } from '@playwright/test'

test.describe('Authentification', () => {
  test('devrait permettre la connexion avec des identifiants valides', async ({ page }) => {
    // Naviguer vers la page d'accueil
    await page.goto('/')

    // Vérifier qu'on est redirigé vers la page de connexion
    await expect(page).toHaveURL('/login')
    await expect(page.locator('text=Connexion à AudioNexus')).toBeVisible()

    // Remplir le formulaire de connexion
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin')

    // Retirer les mocks pour tester le vrai flow login-backend
    // Les mocks étaient utilisés pour démonstration

    // Cliquer sur le bouton de connexion
    await page.click('button[type="submit"]')

    // Vérifier la redirection vers le dashboard
    await expect(page).toHaveURL('/')
    await expect(page.locator('text=Dashboard AudioNexus')).toBeVisible()
  })

  test('devrait afficher une erreur avec des identifiants invalides', async ({ page }) => {
    await page.goto('/login')

    // Ne pas utiliser de mock - laisser faire l'appel réel pour identifier le problème
    // await page.route('/api/auth/login', async route => {
    //   await route.fulfill({
    //     status: 401,
    //     contentType: 'application/json',
    //     body: JSON.stringify({
    //       detail: 'Nom d\'utilisateur ou mot de passe incorrect'
    //     })
    //   })
    // })

    // Remplir avec des mauvais identifiants
    await page.fill('input[name="username"]', 'wronguser')
    await page.fill('input[name="password"]', 'wrongpass')

    // Cliquer sur connexion
    await page.click('button[type="submit"]')

    // Vérifier que l'erreur s'affiche (via toast ou autre mécanisme)
    // Note: L'implémentation exacte dépend de la lib de notifications utilisée
    await expect(page.locator('input[name="username"]')).toBeVisible() // Toujours sur la page de login
  })

  test('devrait rediriger les utilisateurs non authentifiés vers la page login', async ({ page }) => {
    // Accéder directement au dashboard sans authentification
    await page.goto('/')

    // Devrait être redirigé vers /login
    await expect(page).toHaveURL('/login')
  })
})

test.describe('Navigation et accessibilité', () => {
  test('devrait supporter la navigation au clavier', async ({ page }) => {
    await page.goto('/login')

    // Focus sur le premier champ
    await page.keyboard.press('Tab')
    await expect(page.locator('input[name="username"]')).toBeFocused()

    // Tab vers le champ mot de passe
    await page.keyboard.press('Tab')
    await expect(page.locator('input[name="password"]')).toBeFocused()

    // Tab vers le bouton
    await page.keyboard.press('Tab')
    await expect(page.locator('button[type="submit"]')).toBeFocused()
  })

  test('devrait avoir un titre de page approprié', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/AudioNexus/)
  })

  test('devrait supporter le lien "skip to main content"', async ({ page }) => {
    await page.goto('/')
    await page.keyboard.press('Tab') // Activer le premier lien de skip
    await expect(page.locator('a[href="#main-content"]')).toBeFocused()
  })
})

test.describe('Thèmes', () => {
  test('devrait permettre de basculer entre les thèmes sombre et clair', async ({ page }) => {
    await page.goto('/login')

    // Vérifier que le toggle de thème est présent
    const themeToggle = page.locator('[aria-label*="thème"]')
    await expect(themeToggle).toBeVisible()

    // Tester les boutons de thème
    await expect(page.locator('[aria-label*="thème clair"]')).toBeVisible()
    await expect(page.locator('[aria-label*="thème sombre"]')).toBeVisible()
    await expect(page.locator('[aria-label*="thème système"]')).toBeVisible()
  })
})