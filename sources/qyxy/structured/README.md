### Mysql's Configs

    create database clawer
    # edit structured/settings.py
    # change `db_user` and `db_password` for yours.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'clawer',
            'USER': 'db_user',
            'PASSWORD': 'db_password',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }

### Create Mysql Tables

    python manage.py makemigrations
    python manage.py migrate

### Import Data to Database

    python manage.py structured

### Json Keys to Mysql Tables

    ind_comm_pub_reg_basic                   => basic
    ind_comm_pub_arch_liquidation            => industry_commerce_clear

    ind_comm_pub_reg_shareholder             => industry_commerce_shareholders
    ind_comm_pub_reg_modify                  => industry_commerce_change
    ind_comm_pub_arch_key_persons            => industry_commerce_mainperson
    ind_comm_pub_arch_branch                 => industry_commerce_branch
    ind_comm_pub_movable_property_reg        => industry_commerce_mortgage
    ind_comm_pub_equity_ownership_reg        => industry_mortgage_detail_mortgagee
    ind_comm_pub_administration_sanction     => industry_commerce_administrative_penalty
    ind_comm_pub_business_exception          => industry_commerce_exception
    ind_comm_pub_serious_violate_law         => industry_commerce_illegal
    ind_comm_pub_spot_check                  => industry_commerce_check

    ent_pub_ent_annual_report                => enter_annual_report
                                             => year_report_sharechange
                                             => year_report_online
                                             => year_report_investment
                                             => year_report_modification
                                             => year_report_assets
                                             => year_report_shareholder
                                             => year_report_basic
                                             => year_report_correct

    ent_pub_shareholder_capital_contribution => enter_shareholder
    ent_pub_equity_change                    => enter_sharechange
    ent_pub_administration_license           => enter_administrative_license
    ent_pub_knowledge_property               => enter_intellectual_property_pledge
    ent_pub_administration_sanction          => enter_administrative_penalty

    other_dept_pub_administration_license    => other_administrative_license
    other_dept_pub_administration_sanction   => other_administrative_penalty

    judical_assist_pub_equity_freeze         => judicial_share_freeze
    judical_assist_pub_shareholder_modify    => judicial_shareholder_change
