# Copyright (C) 2022  Red Hat, Inc.

# This software is licensed to you under the GNU General Public License,
# version 3 (GPLv3). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv3
# along with this software; if not, see
# https://www.gnu.org/licenses/gpl-3.0.txt.

"""factories to help testing Quipucords."""

from unittest import mock

import pytest

from api.models import DeploymentsReport, Source, SourceOptions, SystemFingerprint
from tests.factories import DeploymentReportFactory, SourceFactory


@pytest.mark.django_db
class TestDeploymentsReportFactoryFingerprints:
    """Test DeploymentsReportFactory.number_of_fingerprints method."""

    @pytest.mark.parametrize(
        "factory_method", [DeploymentReportFactory.create, DeploymentReportFactory]
    )
    def test_create_setting_number(self, factory_method):
        """Test setting number_of fingerprints when creating a deployment report."""
        deployment_report = factory_method(number_of_fingerprints=10)
        assert len(deployment_report.system_fingerprints.all()) == 10
        assert DeploymentsReport.objects.all().count() == 1
        assert SystemFingerprint.objects.all().count() == 10

    def test_build_setting_number(self):
        """Check for failure when setting number of fingerprints with build method."""
        with pytest.raises(ValueError):
            DeploymentReportFactory.build(number_of_fingerprints=1)

    @mock.patch("tests.factories.random.randint", return_value=1)
    def test_create_with_defaults(self, patched_randint):
        """Test related fingerprint creation without default values."""
        DeploymentReportFactory.create()
        assert patched_randint.mock_calls == [mock.call(1, 5)]
        assert DeploymentsReport.objects.all().count() == 1
        assert SystemFingerprint.objects.all().count() == 1

    @mock.patch("tests.factories.random.randint")
    def test_build_with_defaults(self, patched_randint):
        """Check no fingerprints are created when using build."""
        instance = DeploymentReportFactory.build()
        assert patched_randint.mock_calls == []
        assert instance.id is None
        assert DeploymentsReport.objects.all().count() == 0
        assert SystemFingerprint.objects.all().count() == 0
        # saving deployment won't create fingerprints
        instance.save()
        assert instance.id
        assert SystemFingerprint.objects.all().count() == 0

    def test_create_batch_setting_number(self):
        """Test creating a bach of deployment reports also creates fingerprints."""
        instances = DeploymentReportFactory.create_batch(
            size=10, number_of_fingerprints=10
        )

        assert instances[0].system_fingerprints.count() == 10
        assert DeploymentsReport.objects.all().count() == 10
        assert SystemFingerprint.objects.all().count() == 100


@pytest.mark.django_db
class TestDeploymentReportFactoryReportID:
    """Test DeploymentReport.set_report_id post generation method."""

    @pytest.mark.parametrize(
        "factory_method", [DeploymentReportFactory, DeploymentReportFactory.create]
    )
    def test_create(self, factory_method):
        """Check report_id matches model pk."""
        deployments_report = factory_method()
        assert deployments_report.id
        assert deployments_report.id == deployments_report.report_id

    def test_create_batch(self):
        """Check report_id matches model pk using create_batch method."""
        deployments_reports = DeploymentReportFactory.create_batch(size=2)
        assert all(d.id for d in deployments_reports)
        assert all(d.id == d.report_id for d in deployments_reports)

    def test_build(self):
        """Check report_id with instances created by build method."""
        deployments_report: DeploymentsReport = DeploymentReportFactory.build()
        assert deployments_report.id is None
        assert deployments_report.report_id == deployments_report.id
        # save instance to db. it should have got an id
        deployments_report.save()
        assert deployments_report.id
        # using build method report_id won't match pk
        assert deployments_report.id != deployments_report.report_id


@pytest.mark.django_db
class TestSourceFactory:
    """Test SourceFactory."""

    def test_option_default(self):
        """Test SourceFactory option default behavior."""
        source = SourceFactory()
        assert isinstance(source, Source)
        assert source.id
        assert isinstance(source.options, SourceOptions)
        assert source.options.id

    def test_option_none(self):
        """Test SourceFactory option set to none."""
        source = SourceFactory(options=None)
        assert isinstance(source, Source)
        assert source.id
        assert source.options is None
