# Generated by Django 4.2.7 on 2023-11-28 20:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('superadmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=False)),
                ('voting_admins', models.ManyToManyField(related_name='elections', to='superadmin.vote_admins')),
            ],
        ),
        migrations.CreateModel(
            name='Positions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Pos_name', models.CharField(max_length=100)),
                ('Num_Candidates', models.IntegerField(default=0)),
                ('Total_votes', models.IntegerField(default=0)),
                ('max_candidates_elected', models.PositiveIntegerField()),
                ('election', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='VotingAdmin.election')),
                ('voting_admins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins')),
            ],
        ),
        migrations.CreateModel(
            name='VoterProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_code', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('voting_admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins')),
            ],
        ),
        migrations.CreateModel(
            name='VoteLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('candidate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='VotingAdmin.candidate')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VotingAdmin.election')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VotingAdmin.positions')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Partylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Party_name', models.CharField(max_length=150)),
                ('Logo', models.ImageField(upload_to='')),
                ('Description', models.TextField(blank=True)),
                ('voting_admins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=255)),
                ('field_type', models.CharField(max_length=50)),
                ('is_required', models.BooleanField(default=False)),
                ('choices', models.JSONField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('voting_admins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='CSVUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('data', models.JSONField()),
                ('header_order', models.JSONField()),
                ('voting_admins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins')),
            ],
        ),
        migrations.CreateModel(
            name='CandidateApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('election', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='VotingAdmin.election')),
                ('partylist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidateapp', to='VotingAdmin.partylist')),
                ('positions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidap', to='VotingAdmin.positions')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('voting_admins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins')),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='application',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='candidate', to='VotingAdmin.candidateapplication'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candid', to='VotingAdmin.election'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='VotingAdmin.positions'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='candidate',
            name='voting_admins',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='superadmin.vote_admins'),
        ),
        migrations.CreateModel(
            name='VoterElection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_voted', models.BooleanField(default=False)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VotingAdmin.election')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('voter', 'election')},
            },
        ),
    ]
