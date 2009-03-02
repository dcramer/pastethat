{% if user %}
    <?php if ($user->isAuthenticated()) { ?>
        <p>Logged in as <a href="<?=$user->getSettingsUrl();?>"><?=htmlentities($user->getName());?></a>. (<a href="<?=UserModel::getLogoutUrl();?>">Change User</a>)</p>
    <?php } else { ?>
        <p>Logged in as <em>Guest</em>. (<a href="<?=UserModel::getLogoutUrl();?>">Change User</a>)</p>
    <?php } ?>