from pathlib import Path

scripts_dir = Path(r"D:\antigravityStudy\StarInvader\Assets\Scripts")
editor_dir = scripts_dir / "Editor"
scripts_dir.mkdir(parents=True, exist_ok=True)
editor_dir.mkdir(parents=True, exist_ok=True)

# 1. SoundManager.cs
sound_manager_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// BGM 및 SFX 사운드 재생 관리 매니저 (sound_manager.py 대응)
    /// </summary>
    public class SoundManager : MonoBehaviour
    {
        public static SoundManager Instance { get; private set; }

        [Header("오디오 클립")]
        [SerializeField] private AudioClip shootClip;
        [SerializeField] private AudioClip explosionClip;
        [SerializeField] private AudioClip hitClip;

        private AudioSource sfxSource;

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
                return;
            }

            sfxSource = gameObject.AddComponent<AudioSource>();
            sfxSource.playOnAwake = false;

            // 폭발음 클립이 없을 경우 절차적 신스 폭발음 생성
            if (explosionClip == null)
            {
                explosionClip = GenerateProceduralExplosionClip();
            }
        }

        public void PlayShootSound()
        {
            if (shootClip != null)
            {
                sfxSource.PlayOneShot(shootClip, 0.7f);
            }
        }

        public void PlayExplosionSound()
        {
            if (explosionClip != null)
            {
                sfxSource.PlayOneShot(explosionClip, 0.85f);
            }
        }

        public void PlayHitSound()
        {
            if (hitClip != null)
            {
                sfxSource.PlayOneShot(hitClip, 0.8f);
            }
            else
            {
                PlayExplosionSound();
            }
        }

        private AudioClip GenerateProceduralExplosionClip()
        {
            int sampleRate = 44100;
            float duration = 0.35f;
            int totalSamples = (int)(sampleRate * duration);
            float[] samples = new float[totalSamples];

            for (int i = 0; i < totalSamples; i++)
            {
                float t = (float)i / totalSamples;
                float noise = (Random.value * 2f - 1f);
                float decay = Mathf.Exp(-t * 8f);
                samples[i] = noise * decay;
            }

            AudioClip clip = AudioClip.Create("SynthExplosion", totalSamples, 1, sampleRate, false);
            clip.SetData(samples, 0);
            return clip;
        }
    }
}
"""
(scripts_dir / "SoundManager.cs").write_text(sound_manager_code, encoding="utf-8")

# 2. CameraShake.cs
camera_shake_code = """using System.Collections;
using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 피격 및 폭발 시 카메라 흔들림 연출
    /// </summary>
    public class CameraShake : MonoBehaviour
    {
        public static CameraShake Instance { get; private set; }

        private Vector3 originalPos;
        private Coroutine shakeCoroutine;

        private void Awake()
        {
            if (Instance == null) Instance = this;
            else Destroy(gameObject);

            originalPos = transform.localPosition;
        }

        public void TriggerShake(float duration = 0.2f, float magnitude = 0.18f)
        {
            if (shakeCoroutine != null) StopCoroutine(shakeCoroutine);
            shakeCoroutine = StartCoroutine(ShakeRoutine(duration, magnitude));
        }

        private IEnumerator ShakeRoutine(float duration, float magnitude)
        {
            float elapsed = 0f;

            while (elapsed < duration)
            {
                float x = Random.Range(-1f, 1f) * magnitude;
                float y = Random.Range(-1f, 1f) * magnitude;

                transform.localPosition = new Vector3(originalPos.x + x, originalPos.y + y, originalPos.z);

                elapsed += Time.deltaTime;
                yield return null;
            }

            transform.localPosition = originalPos;
            shakeCoroutine = null;
        }
    }
}
"""
(scripts_dir / "CameraShake.cs").write_text(camera_shake_code, encoding="utf-8")

# 3. BackgroundScroller.cs
bg_scroller_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 우주 배경 무한 세로 스크롤 연출 (bg_space.png 대응)
    /// </summary>
    public class BackgroundScroller : MonoBehaviour
    {
        [Header("스크롤 설정")]
        [SerializeField] private float scrollSpeed = 1.2f;
        [SerializeField] private float resetHeight = 10.0f;

        [Header("배경 레이어들 (위/아래 2장)")]
        [SerializeField] private Transform bg1;
        [SerializeField] private Transform bg2;

        private void Update()
        {
            if (bg1 == null || bg2 == null) return;

            float delta = scrollSpeed * Time.deltaTime;
            bg1.position += Vector3.down * delta;
            bg2.position += Vector3.down * delta;

            // 화면 아래로 벗어난 배경을 다시 위쪽으로 재배치
            if (bg1.position.y <= -resetHeight)
            {
                bg1.position = new Vector3(bg1.position.x, bg2.position.y + resetHeight, bg1.position.z);
            }

            if (bg2.position.y <= -resetHeight)
            {
                bg2.position = new Vector3(bg2.position.x, bg1.position.y + resetHeight, bg2.position.z);
            }
        }
    }
}
"""
(scripts_dir / "BackgroundScroller.cs").write_text(bg_scroller_code, encoding="utf-8")

# 4. ExplosionEffect.cs
explosion_code = """using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 적 파괴 시 폭발 애니메이션 및 자동 파괴
    /// </summary>
    public class ExplosionEffect : MonoBehaviour
    {
        [SerializeField] private float lifeTime = 0.4f;
        [SerializeField] private float expandSpeed = 2.5f;

        private SpriteRenderer sr;
        private float timer = 0f;
        private Color initialColor;

        private void Awake()
        {
            sr = GetComponent<SpriteRenderer>();
            if (sr != null) initialColor = sr.color;
        }

        private void Update()
        {
            timer += Time.deltaTime;
            float progress = timer / lifeTime;

            // 점점 커지면서 투명해지는 연출
            transform.localScale += Vector3.one * (expandSpeed * Time.deltaTime);

            if (sr != null)
            {
                Color c = initialColor;
                c.a = Mathf.Lerp(1f, 0f, progress);
                sr.color = c;
            }

            if (timer >= lifeTime)
            {
                Destroy(gameObject);
            }
        }
    }
}
"""
(scripts_dir / "ExplosionEffect.cs").write_text(explosion_code, encoding="utf-8")

# 5. Update Enemy.cs with Explosion and SFX
enemy_code = """using System;
using UnityEngine;

namespace StarInvader
{
    public enum EnemyType
    {
        Top,
        Mid,
        Bottom
    }

    /// <summary>
    /// 개별 적 기체 컴포넌트 (피격 시 폭발 및 사운드 연동)
    /// </summary>
    public class Enemy : MonoBehaviour
    {
        [Header("적 속성")]
        [SerializeField] private EnemyType enemyType = EnemyType.Bottom;
        [SerializeField] private int scoreValue = GameConstants.SCORE_PER_ENEMY;
        [SerializeField] private int maxHp = 1;
        [SerializeField] private GameObject explosionPrefab;

        private int currentHp;
        public event Action<Enemy> OnDestroyed;

        private void Awake()
        {
            currentHp = maxHp;
        }

        public void Setup(EnemyType type, int score = GameConstants.SCORE_PER_ENEMY, GameObject explosion = null)
        {
            enemyType = type;
            scoreValue = score;
            if (explosion != null) explosionPrefab = explosion;
        }

        public void TakeDamage(int damage = 1)
        {
            currentHp -= damage;
            if (currentHp <= 0)
            {
                Die();
            }
        }

        private void Die()
        {
            // 폭발 이펙트 생성
            if (explosionPrefab != null)
            {
                Instantiate(explosionPrefab, transform.position, Quaternion.identity);
            }

            // 폭발 사운드 재생
            if (SoundManager.Instance != null)
            {
                SoundManager.Instance.PlayExplosionSound();
            }

            OnDestroyed?.Invoke(this);
            Destroy(gameObject);
        }

        public EnemyType Type => enemyType;
        public int ScoreValue => scoreValue;
    }
}
"""
(scripts_dir / "Enemy.cs").write_text(enemy_code, encoding="utf-8")

# 6. Update PlayerController.cs with Shoot SFX and Screen Shake on hit
player_code = """using System;
using System.Collections;
using UnityEngine;

namespace StarInvader
{
    /// <summary>
    /// 플레이어 이동, 사격(SFX), 피격(CameraShake), 무적 제어
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [Header("이동 설정")]
        [SerializeField] private float moveSpeed = GameConstants.PLAYER_SPEED;
        [SerializeField] private float minX = -GameConstants.SCREEN_WIDTH_HALF;
        [SerializeField] private float maxX = GameConstants.SCREEN_WIDTH_HALF;

        [Header("발사 설정")]
        [SerializeField] private GameObject bulletPrefab;
        [SerializeField] private Transform firePoint;
        [SerializeField] private float shootCooldown = GameConstants.PLAYER_SHOOT_COOLDOWN;
        [SerializeField] private int maxConcurrentBullets = GameConstants.PLAYER_MAX_BULLETS;

        [Header("라이프 및 무적 설정")]
        [SerializeField] private int maxLives = GameConstants.PLAYER_MAX_LIVES;
        [SerializeField] private float invincibleDuration = GameConstants.PLAYER_INVINCIBLE_DURATION;

        private int currentLives;
        private bool isInvincible = false;
        private float lastShootTime = -10f;
        private SpriteRenderer spriteRenderer;

        public event Action<int> OnLivesChanged;
        public event Action OnPlayerDied;

        private void Awake()
        {
            currentLives = maxLives;
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        private void Start()
        {
            if (firePoint == null)
            {
                GameObject fp = new GameObject("FirePoint");
                fp.transform.SetParent(transform);
                fp.transform.localPosition = new Vector3(0, 0.5f, 0);
                firePoint = fp.transform;
            }

            OnLivesChanged?.Invoke(currentLives);
        }

        private void Update()
        {
            HandleMovement();
            HandleShooting();
        }

        private void HandleMovement()
        {
            float horizontalInput = Input.GetAxisRaw("Horizontal");
            Vector3 position = transform.position;
            position.x += horizontalInput * moveSpeed * Time.deltaTime;
            position.x = Mathf.Clamp(position.x, minX, maxX);
            transform.position = position;
        }

        private void HandleShooting()
        {
            if (Input.GetKey(KeyCode.Space) || Input.GetButton("Fire1"))
            {
                if (Time.time >= lastShootTime + shootCooldown)
                {
                    int activeBulletCount = 0;
                    Bullet[] existingBullets = FindObjectsByType<Bullet>(FindObjectsSortMode.None);
                    foreach (var b in existingBullets)
                    {
                        if (!b.IsEnemyBullet) activeBulletCount++;
                    }

                    if (activeBulletCount < maxConcurrentBullets)
                    {
                        Shoot();
                    }
                }
            }
        }

        private void Shoot()
        {
            lastShootTime = Time.time;

            if (bulletPrefab != null)
            {
                Instantiate(bulletPrefab, firePoint.position, Quaternion.identity);
            }

            // 발사음 재생
            if (SoundManager.Instance != null)
            {
                SoundManager.Instance.PlayShootSound();
            }
        }

        public void TakeDamage(int damage = 1)
        {
            if (isInvincible || currentLives <= 0) return;

            currentLives -= damage;
            OnLivesChanged?.Invoke(currentLives);

            // 카메라 셰이크 연출
            if (CameraShake.Instance != null)
            {
                CameraShake.Instance.TriggerShake(0.25f, 0.2f);
            }

            // 피격 사운드
            if (SoundManager.Instance != null)
            {
                SoundManager.Instance.PlayHitSound();
            }

            if (currentLives <= 0)
            {
                Die();
            }
            else
            {
                StartCoroutine(InvincibilityRoutine());
            }
        }

        private IEnumerator InvincibilityRoutine()
        {
            isInvincible = true;
            float elapsed = 0f;
            float flashInterval = 0.1f;

            while (elapsed < invincibleDuration)
            {
                if (spriteRenderer != null)
                {
                    spriteRenderer.enabled = !spriteRenderer.enabled;
                }
                yield return new WaitForSeconds(flashInterval);
                elapsed += flashInterval;
            }

            if (spriteRenderer != null)
            {
                spriteRenderer.enabled = true;
            }
            isInvincible = false;
        }

        private void Die()
        {
            OnPlayerDied?.Invoke();
            gameObject.SetActive(false);
        }

        public int CurrentLives => currentLives;
        public bool IsInvincible => isInvincible;
    }
}
"""
(scripts_dir / "PlayerController.cs").write_text(player_code, encoding="utf-8")

# 7. Update StarInvaderSetupTool.cs with Step 4 Menu
editor_setup_code = """using UnityEngine;
using UnityEditor;
using System.IO;

namespace StarInvader.Editor
{
    public class StarInvaderSetupTool : EditorWindow
    {
        [MenuItem("Star Invader/1단계: 플레이어 및 씬 자동 구성", false, 1)]
        public static void SetupStep1Scene()
        {
            SetupCamera();
            GameObject bulletPrefabObj = SetupBulletPrefab();
            SetupPlayer(bulletPrefabObj);

            EditorUtility.DisplayDialog("Star Invader", "1단계 (카메라, 플레이어, 탄환) 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        [MenuItem("Star Invader/2단계: 적 편대 및 충돌 시스템 구성", false, 2)]
        public static void SetupStep2Scene()
        {
            SetupStep3SceneInternal(false);
            EditorUtility.DisplayDialog("Star Invader", "2단계 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        [MenuItem("Star Invader/3단계: 적 공격 및 플레이어 라이프 시스템 구성", false, 3)]
        public static void SetupStep3Scene()
        {
            SetupStep3SceneInternal(true);
            EditorUtility.DisplayDialog("Star Invader", "3단계 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        [MenuItem("Star Invader/4단계: 사운드 및 이펙트/배경 연출 구성", false, 4)]
        public static void SetupStep4Scene()
        {
            // 1. 카메라 & 카메라 셰이크
            Camera mainCam = SetupCamera();
            if (mainCam.GetComponent<CameraShake>() == null)
            {
                mainCam.gameObject.AddComponent<CameraShake>();
            }

            // 2. 우주 배경 스크롤러 세팅
            SetupBackground();

            // 3. 사운드 매니저 세팅
            SetupSoundManager();

            // 4. 폭발 프리팹 생성
            GameObject explosionPrefab = SetupExplosionPrefab();

            // 5. 플레이어 & 적 편대 세팅 (폭발 프리팹 포함)
            GameObject bulletPrefabObj = SetupBulletPrefab();
            SetupPlayer(bulletPrefabObj);
            SetupStep3SceneInternal(true, explosionPrefab);

            EditorUtility.DisplayDialog("Star Invader", "4단계 (사운드, 폭발 이펙트, 우주 배경 스크롤링, 피격 시 카메라 흔들림) 구성이 완료되었습니다!\\n\\n유니티 상단의 [▶ (Play)] 버튼을 눌러 테스트해 보세요.", "확인");
        }

        private static Camera SetupCamera()
        {
            Camera mainCam = Camera.main;
            if (mainCam == null)
            {
                GameObject camObj = new GameObject("Main Camera");
                mainCam = camObj.AddComponent<Camera>();
                camObj.tag = "MainCamera";
            }

            mainCam.orthographic = true;
            mainCam.orthographicSize = 5f;
            mainCam.transform.position = new Vector3(0, 0, -10f);
            mainCam.backgroundColor = new Color(0.04f, 0.04f, 0.08f, 1f);
            mainCam.clearFlags = CameraClearFlags.SolidColor;
            return mainCam;
        }

        private static void SetupBackground()
        {
            GameObject bgParent = GameObject.Find("Background");
            if (bgParent == null) bgParent = new GameObject("Background");

            string bgSpritePath = "Assets/GameAssets/images/background/bg_space.png";
            EnsureSpriteImport(bgSpritePath);
            Sprite bgSprite = AssetDatabase.LoadAssetAtPath<Sprite>(bgSpritePath);

            Transform bg1 = bgParent.transform.Find("BG_Layer1");
            if (bg1 == null)
            {
                GameObject b1 = new GameObject("BG_Layer1");
                b1.transform.SetParent(bgParent.transform);
                b1.transform.position = Vector3.zero;
                SpriteRenderer sr1 = b1.AddComponent<SpriteRenderer>();
                sr1.sprite = bgSprite;
                sr1.sortingOrder = -10;
                bg1 = b1.transform;
            }

            Transform bg2 = bgParent.transform.Find("BG_Layer2");
            if (bg2 == null)
            {
                GameObject b2 = new GameObject("BG_Layer2");
                b2.transform.SetParent(bgParent.transform);
                b2.transform.position = new Vector3(0, 10f, 0);
                SpriteRenderer sr2 = b2.AddComponent<SpriteRenderer>();
                sr2.sprite = bgSprite;
                sr2.sortingOrder = -10;
                bg2 = b2.transform;
            }

            BackgroundScroller scroller = bgParent.GetComponent<BackgroundScroller>();
            if (scroller == null) scroller = bgParent.AddComponent<BackgroundScroller>();

            SerializedObject serializedBg = new SerializedObject(scroller);
            serializedBg.FindProperty("bg1").objectReferenceValue = bg1;
            serializedBg.FindProperty("bg2").objectReferenceValue = bg2;
            serializedBg.ApplyModifiedProperties();
        }

        private static void SetupSoundManager()
        {
            GameObject smObj = GameObject.Find("SoundManager");
            if (smObj == null) smObj = new GameObject("SoundManager");

            SoundManager sm = smObj.GetComponent<SoundManager>();
            if (sm == null) sm = smObj.AddComponent<SoundManager>();

            string shootSoundPath = "Assets/GameAssets/sounds/laser_shoot.wav";
            AudioClip shootClip = AssetDatabase.LoadAssetAtPath<AudioClip>(shootSoundPath);

            SerializedObject serializedSm = new SerializedObject(sm);
            if (shootClip != null)
            {
                serializedSm.FindProperty("shootClip").objectReferenceValue = shootClip;
            }
            serializedSm.ApplyModifiedProperties();
        }

        private static GameObject SetupExplosionPrefab()
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string prefabPath = "Assets/Prefabs/ExplosionEffect.prefab";
            GameObject expPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (expPrefab == null)
            {
                GameObject tempExp = new GameObject("ExplosionEffect");
                SpriteRenderer sr = tempExp.AddComponent<SpriteRenderer>();
                sr.sortingOrder = 5;

                string expSpritePath = "Assets/GameAssets/images/effects/explosion.png";
                EnsureSpriteImport(expSpritePath);
                Sprite expSprite = AssetDatabase.LoadAssetAtPath<Sprite>(expSpritePath);
                if (expSprite != null)
                {
                    sr.sprite = expSprite;
                }
                else
                {
                    sr.color = new Color(1f, 0.7f, 0.2f, 1f);
                    Texture2D tex = MakeColorTexture(32, 32, Color.orange);
                    sr.sprite = Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f), 100f);
                }

                tempExp.AddComponent<ExplosionEffect>();

                expPrefab = PrefabUtility.SaveAsPrefabAsset(tempExp, prefabPath);
                GameObject.DestroyImmediate(tempExp);
            }
            return expPrefab;
        }

        private static void SetupStep3SceneInternal(bool includeEnemyBullets, GameObject explosionPrefab = null)
        {
            SetupCamera();
            GameObject bulletPrefabObj = SetupBulletPrefab();
            SetupPlayer(bulletPrefabObj);

            GameObject topEnemyPrefab = SetupEnemyPrefab("Enemy_Top", "Assets/GameAssets/images/enemy/enemy_top.png", EnemyType.Top, Color.magenta, explosionPrefab);
            GameObject midEnemyPrefab = SetupEnemyPrefab("Enemy_Mid", "Assets/GameAssets/images/enemy/enemy_mid.png", EnemyType.Mid, new Color(1f, 0.6f, 0.2f), explosionPrefab);
            GameObject bottomEnemyPrefab = SetupEnemyPrefab("Enemy_Bottom", "Assets/GameAssets/images/enemy/enemy_bottom.png", EnemyType.Bottom, Color.yellow, explosionPrefab);
            GameObject enemyBulletPrefab = SetupEnemyBulletPrefab();

            GameObject fleetObj = GameObject.Find("EnemyFleet");
            if (fleetObj == null)
            {
                fleetObj = new GameObject("EnemyFleet");
            }

            EnemyFleet fleet = fleetObj.GetComponent<EnemyFleet>();
            if (fleet == null) fleet = fleetObj.AddComponent<EnemyFleet>();

            SerializedObject serializedFleet = new SerializedObject(fleet);
            serializedFleet.FindProperty("topEnemyPrefab").objectReferenceValue = topEnemyPrefab;
            serializedFleet.FindProperty("midEnemyPrefab").objectReferenceValue = midEnemyPrefab;
            serializedFleet.FindProperty("bottomEnemyPrefab").objectReferenceValue = bottomEnemyPrefab;
            if (includeEnemyBullets)
            {
                serializedFleet.FindProperty("enemyBulletPrefab").objectReferenceValue = enemyBulletPrefab;
            }
            serializedFleet.ApplyModifiedProperties();

            Selection.activeGameObject = fleetObj;
        }

        private static GameObject SetupBulletPrefab()
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string bulletPrefabPath = "Assets/Prefabs/PlayerBullet.prefab";
            GameObject bulletPrefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(bulletPrefabPath);
            if (bulletPrefabObj == null)
            {
                GameObject tempBullet = new GameObject("PlayerBullet");
                SpriteRenderer bSr = tempBullet.AddComponent<SpriteRenderer>();
                bSr.color = new Color(0.47f, 1.0f, 1.0f, 1.0f);
                
                Texture2D bulletTex = MakeColorTexture(16, 40, Color.cyan);
                Sprite bulletSprite = Sprite.Create(bulletTex, new Rect(0, 0, 16, 40), new Vector2(0.5f, 0.5f), 100f);
                bSr.sprite = bulletSprite;

                BoxCollider2D bc = tempBullet.AddComponent<BoxCollider2D>();
                bc.isTrigger = true;
                bc.size = new Vector2(0.16f, 0.4f);

                Bullet b = tempBullet.AddComponent<Bullet>();
                b.SetSpeed(GameConstants.PLAYER_BULLET_SPEED);
                b.SetEnemyBullet(false);

                bulletPrefabObj = PrefabUtility.SaveAsPrefabAsset(tempBullet, bulletPrefabPath);
                GameObject.DestroyImmediate(tempBullet);
            }
            return bulletPrefabObj;
        }

        private static GameObject SetupEnemyBulletPrefab()
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string bulletPrefabPath = "Assets/Prefabs/EnemyBullet.prefab";
            GameObject bulletPrefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(bulletPrefabPath);
            if (bulletPrefabObj == null)
            {
                GameObject tempBullet = new GameObject("EnemyBullet");
                SpriteRenderer bSr = tempBullet.AddComponent<SpriteRenderer>();
                bSr.color = new Color(1.0f, 0.35f, 0.35f, 1.0f);
                
                Texture2D bulletTex = MakeColorTexture(16, 40, Color.red);
                Sprite bulletSprite = Sprite.Create(bulletTex, new Rect(0, 0, 16, 40), new Vector2(0.5f, 0.5f), 100f);
                bSr.sprite = bulletSprite;

                BoxCollider2D bc = tempBullet.AddComponent<BoxCollider2D>();
                bc.isTrigger = true;
                bc.size = new Vector2(0.16f, 0.4f);

                Bullet b = tempBullet.AddComponent<Bullet>();
                b.SetSpeed(GameConstants.ENEMY_BULLET_SPEED);
                b.SetEnemyBullet(true);

                bulletPrefabObj = PrefabUtility.SaveAsPrefabAsset(tempBullet, bulletPrefabPath);
                GameObject.DestroyImmediate(tempBullet);
            }
            return bulletPrefabObj;
        }

        private static void SetupPlayer(GameObject bulletPrefabObj)
        {
            GameObject playerObj = GameObject.Find("Player");
            if (playerObj == null)
            {
                playerObj = new GameObject("Player");
            }

            playerObj.transform.position = new Vector3(0, GameConstants.PLAYER_START_Y, 0);
            SpriteRenderer sr = playerObj.GetComponent<SpriteRenderer>();
            if (sr == null) sr = playerObj.AddComponent<SpriteRenderer>();

            string playerSpritePath = "Assets/GameAssets/images/player/player.png";
            EnsureSpriteImport(playerSpritePath);
            Sprite playerSprite = AssetDatabase.LoadAssetAtPath<Sprite>(playerSpritePath);
            if (playerSprite != null) sr.sprite = playerSprite;

            BoxCollider2D col = playerObj.GetComponent<BoxCollider2D>();
            if (col == null) col = playerObj.AddComponent<BoxCollider2D>();
            col.isTrigger = true;
            col.size = new Vector2(0.5f, 0.4f);

            PlayerController controller = playerObj.GetComponent<PlayerController>();
            if (controller == null) controller = playerObj.AddComponent<PlayerController>();

            SerializedObject serializedPlayer = new SerializedObject(controller);
            SerializedProperty bulletProp = serializedPlayer.FindProperty("bulletPrefab");
            if (bulletProp != null && bulletPrefabObj != null)
            {
                bulletProp.objectReferenceValue = bulletPrefabObj;
                serializedPlayer.ApplyModifiedProperties();
            }
        }

        private static GameObject SetupEnemyPrefab(string name, string spritePath, EnemyType type, Color fallbackColor, GameObject explosionPrefab = null)
        {
            string prefabsDir = "Assets/Prefabs";
            if (!AssetDatabase.IsValidFolder(prefabsDir))
            {
                AssetDatabase.CreateFolder("Assets", "Prefabs");
            }

            string prefabPath = $"Assets/Prefabs/{name}.prefab";
            GameObject prefabObj = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            if (prefabObj == null)
            {
                GameObject tempEnemy = new GameObject(name);
                SpriteRenderer sr = tempEnemy.AddComponent<SpriteRenderer>();

                EnsureSpriteImport(spritePath);
                Sprite enemySprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
                if (enemySprite != null)
                {
                    sr.sprite = enemySprite;
                }
                else
                {
                    sr.color = fallbackColor;
                    Texture2D tex = MakeColorTexture(32, 32, fallbackColor);
                    sr.sprite = Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f), 100f);
                }

                BoxCollider2D col = tempEnemy.AddComponent<BoxCollider2D>();
                col.isTrigger = true;
                col.size = new Vector2(0.4f, 0.32f);

                Enemy enemy = tempEnemy.AddComponent<Enemy>();
                enemy.Setup(type, GameConstants.SCORE_PER_ENEMY, explosionPrefab);

                prefabObj = PrefabUtility.SaveAsPrefabAsset(tempEnemy, prefabPath);
                GameObject.DestroyImmediate(tempEnemy);
            }
            else if (explosionPrefab != null)
            {
                Enemy enemy = prefabObj.GetComponent<Enemy>();
                if (enemy != null)
                {
                    SerializedObject serEnemy = new SerializedObject(enemy);
                    serEnemy.FindProperty("explosionPrefab").objectReferenceValue = explosionPrefab;
                    serEnemy.ApplyModifiedProperties();
                }
            }
            return prefabObj;
        }

        private static void EnsureSpriteImport(string path)
        {
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer != null && importer.textureType != TextureImporterType.Sprite)
            {
                importer.textureType = TextureImporterType.Sprite;
                importer.SaveAndReimport();
            }
        }

        private static Texture2D MakeColorTexture(int width, int height, Color col)
        {
            Texture2D tex = new Texture2D(width, height);
            Color[] pix = new Color[width * height];
            for (int i = 0; i < pix.Length; i++) pix[i] = col;
            tex.SetPixels(pix);
            tex.Apply();
            return tex;
        }
    }
}
"""
(editor_dir / "StarInvaderSetupTool.cs").write_text(editor_setup_code, encoding="utf-8")

print("Step 4 Unity scripts and Editor tool created successfully!")
