import pygame
import sys
import random

# --- FONCTION DE DÉCOUPAGE POUR 16 PIÈCES (Grille 4x4) ---
def decouper_image(chemin_image, lignes=4, colonnes=4):
    image_originale = pygame.image.load(chemin_image).convert()
    
    taille_puzzle = 600
    image_originale = pygame.transform.smoothscale(image_originale, (taille_puzzle, taille_puzzle))
    
    largeur_img, hauteur_img = image_originale.get_size()
    largeur_piece = largeur_img // colonnes
    hauteur_piece = hauteur_img // lignes
    
    depart_x = 200
    depart_y = 10
    marge = 30  # Marge adaptée pour les ergots de 16 pièces
    
    pieces = []
    
    for r in range(lignes):
        for c in range(colonnes):
            rect_piece = pygame.Rect(c * largeur_piece, r * hauteur_piece, largeur_piece, hauteur_piece)
            
            surf_largeur = largeur_piece + (2 * marge)
            surf_hauteur = hauteur_piece + (2 * marge)
            
            piece_surf = pygame.Surface((surf_largeur, surf_hauteur), pygame.SRCALPHA)
            mask_surf = pygame.Surface((surf_largeur, surf_hauteur), pygame.SRCALPHA)
            
            # Corps de base de la pièce
            pygame.draw.rect(mask_surf, (255, 255, 255, 255), (marge, marge, largeur_piece, hauteur_piece))
            
            cx, cy = marge + largeur_piece // 2, marge + hauteur_piece // 2
            
            # Ergots et encoches adaptés pour 4x4
            if c < colonnes - 1:
                pygame.draw.circle(mask_surf, (255, 255, 255, 255), (marge + largeur_piece, cy), 12)
            if c > 0:
                pygame.draw.circle(mask_surf, (0, 0, 0, 0), (marge, cy), 12)
                
            if r < lignes - 1:
                pygame.draw.circle(mask_surf, (255, 255, 255, 255), (cx, marge + hauteur_piece), 12)
            if r > 0:
                pygame.draw.circle(mask_surf, (0, 0, 0, 0), (cx, marge), 12)

            piece_surf.blit(image_originale, (marge - c * largeur_piece, marge - r * hauteur_piece))
            piece_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            rect_final = pygame.Rect(
                depart_x + c * largeur_piece - marge,
                depart_y + r * hauteur_piece - marge,
                surf_largeur,
                surf_hauteur
            )
            rect_correct = pygame.Rect(
                depart_x + c * largeur_piece,
                depart_y + r * hauteur_piece,
                largeur_piece,
                hauteur_piece
            )

            pieces.append({
                "surface": piece_surf,
                "rect": rect_final,
                "rect_correct": rect_correct,
                "bien_placee": False
            })
            
    return pieces

# --- FONCTION PRINCIPALE DU JEU ---
def lancer_jeu_puzzle(niveau_initial=1):
    pygame.init()
    
    LARGEUR, HAUTEUR = 1000, 600
    fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Nova - L'Étoile | Arena Multijoueur")

    VERT = (46, 204, 113)

    # --- STYLE TAPIS DE FEUTRINE PRO ---
    COULEUR_TAPIS_FOND = (30, 35, 45)      # Gris-bleu mat très élégant pour l'arrière-plan général
    COULEUR_ZONE_JEU = (22, 26, 34)       # Fond légèrement plus sombre pour la zone centrale du puzzle
    COULEUR_CADRE = (70, 85, 110)         # Bordure subtile et propre

    nb_niveaux_choisi = 10 
    les_niveaux_du_jeu = {}
    for i in range(1, nb_niveaux_choisi + 1):
        chemin = f"images/niveau{i}.jpg"
        try:
            les_niveaux_du_jeu[i] = decouper_image(chemin, 4, 4)
        except FileNotFoundError:
            print(f"Attention : {chemin} introuvable.")

    def charger_niveau(num_niveau):
        donnees_pieces = les_niveaux_du_jeu[num_niveau]
        positions = []
        total_pieces = len(donnees_pieces)  # 16 pièces
        
        for index, data in enumerate(donnees_pieces):
            rect_actuel = data["surface"].get_rect()
            
            # Répartition des 16 pièces sur les côtés (8 à gauche, 8 à droite)
            moitie = total_pieces // 2
            if index < moitie:
                rect_actuel.x = 10 + (index % 2) * 85
                rect_actuel.y = 20 + (index // 2) * 65
            else:
                idx_droite = index - moitie
                rect_actuel.x = 810 + (idx_droite % 2) * 85
                rect_actuel.y = 20 + (idx_droite // 2) * 65
                
            positions.append({
                "surface": data["surface"],
                "rect": rect_actuel,
                "rect_correct": data["rect_correct"],
                "bien_placee": False
            })
        return positions

    niveau_actuel = niveau_initial
    positions_pieces = charger_niveau(niveau_actuel)
    piece_selectionnee = None
    niveau_termine = False

    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False
                pygame.quit()
                return "QUITTE"
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not niveau_termine:
                    if piece_selectionnee is None:
                        for item in positions_pieces:
                            if not item["bien_placee"] and item["rect"].collidepoint(event.pos):
                                piece_selectionnee = item
                                break
                    else:
                        tolerance = 30
                        if abs(piece_selectionnee["rect"].x - (piece_selectionnee["rect_correct"].x - 30)) < tolerance and \
                           abs(piece_selectionnee["rect"].y - (piece_selectionnee["rect_correct"].y - 30)) < tolerance:
                            piece_selectionnee["rect"].topleft = (
                                piece_selectionnee["rect_correct"].x - 30,
                                piece_selectionnee["rect_correct"].y - 30
                            )
                            piece_selectionnee["bien_placee"] = True
                        
                        piece_selectionnee = None
                        
                        toutes_placees = all(item["bien_placee"] for item in positions_pieces)
                        if toutes_placees:
                            niveau_termine = True
                            print(f"Niveau {niveau_actuel} (16 pièces) complété avec succès !")

            elif event.type == pygame.MOUSEMOTION:
                if piece_selectionnee is not None:
                    piece_selectionnee["rect"].center = event.pos

        # 1. Remplissage du fond avec le tapis gris-bleu mat
        fenetre.fill(COULEUR_TAPIS_FOND)
        
        # 2. Dessin de la zone centrale du puzzle (tapis de dépôt) avec son cadre
        if positions_pieces:
            cadre_total = pygame.Rect(200, 10, 600, 600)
            pygame.draw.rect(fenetre, COULEUR_ZONE_JEU, cadre_total)
            pygame.draw.rect(fenetre, COULEUR_CADRE, cadre_total, 2)

        # 3. Affichage des pièces
        for item in positions_pieces:
            fenetre.blit(item["surface"], item["rect"])

        # 4. Message de victoire
        if niveau_termine:
            police = pygame.font.SysFont(None, 48)
            texte_victoire = police.render(f"NOVA - NIVEAU {niveau_actuel} RÉUSSI !", True, VERT)
            fenetre.blit(texte_victoire, (260, 555))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    lancer_jeu_puzzle(1)